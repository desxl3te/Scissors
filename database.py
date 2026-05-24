"""Работа с MySQL-базой проекта Scissors Bar.

Этот модуль больше не меняет схему базы данных на старте приложения.
Backend использует только ту структуру, которая уже определена в
`scissors_bar_dumb.sql`. Если база отсутствует, dump можно импортировать
как исходное состояние проекта, но никаких дополнительных таблиц,
колонок или сидов поверх него здесь не создаётся.
"""

from contextlib import contextmanager
from typing import Dict, Generator

import mysql.connector
from mysql.connector import MySQLConnection

from config import settings


def _base_connection_kwargs(include_database: bool) -> Dict[str, object]:
    """Формирует параметры подключения к MySQL.

    `use_pure=True` оставляем, чтобы штатно импортировать SQL dump
    через `cmd_query_iter` и не получать различающееся поведение драйвера
    между разными типами запросов.
    """

    kwargs: Dict[str, object] = {
        "host": settings.db_host,
        "port": settings.db_port,
        "user": settings.db_user,
        "charset": "utf8mb4",
        "use_pure": True,
    }

    if settings.db_password:
        kwargs["password"] = settings.db_password

    if include_database:
        kwargs["database"] = settings.db_name

    return kwargs


@contextmanager
def get_server_connection() -> Generator[MySQLConnection, None, None]:
    """Открывает соединение к MySQL-серверу без выбора конкретной базы."""

    connection = mysql.connector.connect(**_base_connection_kwargs(include_database=False))

    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


@contextmanager
def get_connection() -> Generator[MySQLConnection, None, None]:
    """Открывает соединение к рабочей базе `scissors_bar`."""

    connection = mysql.connector.connect(**_base_connection_kwargs(include_database=True))

    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def _database_exists() -> bool:
    """Проверяет, существует ли целевая база данных."""

    with get_server_connection() as connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT SCHEMA_NAME
            FROM information_schema.SCHEMATA
            WHERE SCHEMA_NAME = %s
            """,
            (settings.db_name,),
        )
        row = cursor.fetchone()
        cursor.close()

    return row is not None


def _table_exists(connection: MySQLConnection, table_name: str) -> bool:
    """Проверяет, существует ли таблица в рабочей базе."""

    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT TABLE_NAME
        FROM information_schema.TABLES
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
        """,
        (settings.db_name, table_name),
    )
    row = cursor.fetchone()
    cursor.close()
    return row is not None


def _import_dump_if_needed() -> None:
    """Импортирует исходный dump проекта, если база ещё не создана.

    Это не дополнительная миграция, а восстановление штатной схемы проекта
    из уже существующего SQL-файла репозитория.
    """

    if _database_exists():
        return

    if not settings.db_dump_path.exists():
        raise RuntimeError(
            "Не найден SQL dump проекта: "
            f"{settings.db_dump_path}"
        )

    dump_text = settings.db_dump_path.read_text(encoding="utf-8")

    with get_server_connection() as connection:
        for result in connection.cmd_query_iter(dump_text):
            # Если statement вернул строки, mysql-connector требует дочитать их
            # перед выполнением следующего запроса, иначе появится
            # "Unread result found".
            if isinstance(result, dict) and "columns" in result:
                connection.get_rows()


def _ensure_base_tables_exist() -> None:
    """Проверяет, что в базе есть именно базовые таблицы проекта."""

    required_tables = {"menu_items", "secret_menu", "tables", "users", "reservations"}

    with get_connection() as connection:
        missing_tables = [
            table_name for table_name in required_tables if not _table_exists(connection, table_name)
        ]

    if missing_tables:
        raise RuntimeError(
            "В базе отсутствуют обязательные таблицы проекта: "
            + ", ".join(sorted(missing_tables))
        )


def initialize_database() -> None:
    """Подготавливает штатную MySQL-базу к работе backend-а.

    Важно: здесь нет ни `ALTER TABLE`, ни `CREATE TABLE` поверх dump.
    Backend либо работает с уже существующей схемой проекта, либо,
    если база локально отсутствует, поднимает её ровно из `scissors_bar_dumb.sql`.
    """

    _import_dump_if_needed()
    _ensure_base_tables_exist()
