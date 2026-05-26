from mysql.connector import MySQLConnection

from app.core.config import settings
from app.db.connection import get_connection, get_server_connection


def _database_exists() -> bool:
    with get_server_connection() as connection:
        cursor = connection.cursor()
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
    cursor = connection.cursor()
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
    if _database_exists():
        return

    dump_text = settings.db_dump_path.read_text(encoding="utf-8")
    with get_server_connection() as connection:
        for result in connection.cmd_query_iter(dump_text):
            if isinstance(result, dict) and "columns" in result:
                connection.get_rows()


def _ensure_tables() -> None:
    required_tables = {"users", "tables", "reservations", "menu_items", "events"}
    with get_connection() as connection:
        missing = [name for name in required_tables if not _table_exists(connection, name)]

    if missing:
        raise RuntimeError(
            "В базе отсутствуют обязательные таблицы проекта: "
            + ", ".join(sorted(missing))
        )


def initialize_database() -> None:
    _import_dump_if_needed()
    _ensure_tables()
