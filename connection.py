from contextlib import contextmanager
from typing import Generator

import mysql.connector
from mysql.connector import MySQLConnection

from app.core.config import settings


def _connection_kwargs(include_database: bool) -> dict[str, object]:
    kwargs: dict[str, object] = {
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
    connection = mysql.connector.connect(**_connection_kwargs(include_database=False))
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
    connection = mysql.connector.connect(**_connection_kwargs(include_database=True))
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
