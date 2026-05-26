from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Optional

from mysql.connector.errors import IntegrityError

from app.db.connection import get_connection


class ReservationConflictError(Exception):
    """Raised when the database blocks a reservation that lost a race."""


def _fetch_one(
    query: str,
    params: tuple[Any, ...] = (),
    *,
    dictionary: bool = True,
) -> Optional[dict[str, Any]]:
    with get_connection() as connection:
        cursor = connection.cursor(dictionary=dictionary)
        cursor.execute(query, params)
        row = cursor.fetchone()
        cursor.close()
    return row


def _fetch_all(
    query: str,
    params: tuple[Any, ...] = (),
    *,
    dictionary: bool = True,
) -> list[dict[str, Any]]:
    with get_connection() as connection:
        cursor = connection.cursor(dictionary=dictionary)
        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()
    return rows


def _execute(query: str, params: tuple[Any, ...]) -> int:
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(query, params)
        lastrowid = cursor.lastrowid
        cursor.close()
    return int(lastrowid or 0)


# --- Users -----------------------------------------------------------------
# Plain functions are easier to trace in учебный проект: each query lives in
# one place, without service classes or extra state.


def get_user_by_id(user_id: int) -> Optional[dict[str, Any]]:
    return _fetch_one(
        """
        SELECT id, user_name, email, phone, total_visits, created_at, password_hash, role, avatar
        FROM users
        WHERE id = %s
        """,
        (user_id,),
    )


def get_user_by_email(email: str) -> Optional[dict[str, Any]]:
    return _fetch_one(
        """
        SELECT id, user_name, email, phone, total_visits, created_at, password_hash, role, avatar
        FROM users
        WHERE email = %s
        """,
        (email,),
    )


def get_user_by_name(user_name: str) -> Optional[dict[str, Any]]:
    return _fetch_one(
        """
        SELECT id, user_name, email, phone, total_visits, created_at, password_hash, role, avatar
        FROM users
        WHERE user_name = %s
        """,
        (user_name,),
    )

def create_user(
    user_name: str,
    email: str,
    password_hash: str,
    phone: Optional[str],
) -> int:
    return _execute(
        """
        INSERT INTO users (user_name, email, password_hash, phone, total_visits)
        VALUES (%s, %s, %s, %s, 0)
        """,
        (user_name, email, password_hash, phone or None),
    )


def update_user(user_id: int, changes: dict[str, Any]) -> None:
    allowed_fields = ("user_name", "email", "phone", "avatar")
    assignments: list[str] = []
    values: list[Any] = []

    for field_name in allowed_fields:
        if field_name in changes:
            assignments.append(f"{field_name} = %s")
            values.append(changes[field_name] or None)

    if not assignments:
        return

    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            f"""
            UPDATE users
            SET {", ".join(assignments)}
            WHERE id = %s
            """,
            (*values, user_id),
        )
        cursor.close()


# --- Tables and availability -----------------------------------------------


def list_active_tables(min_seats: Optional[int] = None) -> list[dict[str, Any]]:
    query = """
        SELECT id, table_number, seats_count, is_active
        FROM tables
        WHERE is_active = 1
    """
    params: list[Any] = []

    if min_seats is not None:
        query += " AND seats_count >= %s"
        params.append(min_seats)

    query += " ORDER BY seats_count ASC, table_number ASC"
    return _fetch_all(query, tuple(params))


def get_table_by_id(table_id: int) -> Optional[dict[str, Any]]:
    return _fetch_one(
        """
        SELECT id, table_number, seats_count, is_active
        FROM tables
        WHERE id = %s
        """,
        (table_id,),
    )


def _list_confirmed_intervals(table_id: int) -> list[tuple[datetime, datetime]]:
    rows = _fetch_all(
        """
        SELECT reservation_time, duration_hours
        FROM reservations
        WHERE table_id = %s AND status = 'confirmed'
        """,
        (table_id,),
    )

    intervals: list[tuple[datetime, datetime]] = []
    for row in rows:
        start = row["reservation_time"].replace(microsecond=0)
        end = start + timedelta(hours=row["duration_hours"])
        intervals.append((start, end))
    return intervals


def _has_exact_slot_record(table_id: int, reservation_time: datetime) -> bool:
    return _fetch_one(
        """
        SELECT 1 AS marker
        FROM reservations
        WHERE table_id = %s AND reservation_time = %s
        LIMIT 1
        """,
        (table_id, reservation_time),
    ) is not None


def is_table_available(
    table_id: int,
    reservation_time: datetime,
    duration_hours: int,
) -> bool:
    requested_start = reservation_time.replace(microsecond=0)
    requested_end = requested_start + timedelta(hours=duration_hours)

    if _has_exact_slot_record(table_id, requested_start):
        return False

    for existing_start, existing_end in _list_confirmed_intervals(table_id):
        if requested_start < existing_end and existing_start < requested_end:
            return False

    return True


# --- Reservations -----------------------------------------------------------


def create_reservation(
    table_id: int,
    user_id: int,
    reservation_time: datetime,
    duration_hours: int,
    guests_count: int,
    special_request: Optional[str],
) -> int:
    with get_connection() as connection:
        cursor = connection.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO reservations (
                    table_id,
                    user_id,
                    reservation_time,
                    duration_hours,
                    guests_count,
                    status,
                    special_request
                ) VALUES (%s, %s, %s, %s, %s, 'confirmed', %s)
                """,
                (
                    table_id,
                    user_id,
                    reservation_time,
                    duration_hours,
                    guests_count,
                    special_request,
                ),
            )
        except IntegrityError as error:
            cursor.close()
            if error.errno == 1062:
                raise ReservationConflictError(
                    "На выбранное время этот столик уже закреплен в базе."
                ) from error
            raise

        reservation_id = int(cursor.lastrowid or 0)
        cursor.close()

        # Счетчик визитов обновляем в той же транзакции, чтобы бронь и профиль
        # пользователя не расходились между собой.
        visits_cursor = connection.cursor()
        visits_cursor.execute(
            """
            UPDATE users
            SET total_visits = total_visits + 1
            WHERE id = %s
            """,
            (user_id,),
        )
        visits_cursor.close()

    return reservation_id


def get_reservation_by_id(reservation_id: int) -> Optional[dict[str, Any]]:
    return _fetch_one(
        """
        SELECT
            r.id,
            r.table_id,
            r.user_id,
            r.reservation_time,
            r.duration_hours,
            r.guests_count,
            r.status,
            r.special_request,
            t.table_number
        FROM reservations r
        JOIN tables t ON t.id = r.table_id
        WHERE r.id = %s
        """,
        (reservation_id,),
    )


def list_user_reservations(user_id: int) -> list[dict[str, Any]]:
    return _fetch_all(
        """
        SELECT
            r.id,
            r.table_id,
            r.user_id,
            r.reservation_time,
            r.duration_hours,
            r.guests_count,
            r.status,
            r.special_request,
            t.table_number
        FROM reservations r
        JOIN tables t ON t.id = r.table_id
        WHERE r.user_id = %s
        ORDER BY r.reservation_time DESC, r.id DESC
        """,
        (user_id,),
    )


def cancel_reservation(reservation_id: int, user_id: int) -> str:
    with get_connection() as connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id, user_id, status
            FROM reservations
            WHERE id = %s
            """,
            (reservation_id,),
        )
        row = cursor.fetchone()
        cursor.close()

        if row is None:
            return "missing"
        if row["user_id"] != user_id:
            return "forbidden"
        if row["status"] == "cancelled":
            return "already_cancelled"

        update_cursor = connection.cursor()
        update_cursor.execute(
            """
            UPDATE reservations
            SET status = 'cancelled'
            WHERE id = %s
            """,
            (reservation_id,),
        )
        update_cursor.close()

    return "cancelled"


# --- Dashboard --------------------------------------------------------------


def dashboard_snapshot() -> dict[str, Any]:
    with get_connection() as connection:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT COUNT(*) AS total FROM users")
        users_total = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM reservations")
        reservations_total = cursor.fetchone()["total"]

        cursor.execute(
            "SELECT COUNT(*) AS total FROM reservations WHERE status = 'confirmed'"
        )
        confirmed_total = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM tables WHERE is_active = 1")
        active_tables = cursor.fetchone()["total"]

        cursor.execute(
            """
            SELECT status, COUNT(*) AS total
            FROM reservations
            GROUP BY status
            ORDER BY status ASC
            """
        )
        status_rows = cursor.fetchall()

        cursor.execute(
            """
            SELECT DAYNAME(reservation_time) AS weekday, COUNT(*) AS total
            FROM reservations
            GROUP BY weekday
            """
        )
        weekday_rows = cursor.fetchall()

        cursor.execute(
            """
            SELECT t.table_number, COUNT(r.id) AS total
            FROM tables t
            LEFT JOIN reservations r ON r.table_id = t.id
            GROUP BY t.id, t.table_number
            ORDER BY total DESC, t.table_number ASC
            LIMIT 5
            """
        )
        popular_tables = cursor.fetchall()

        cursor.close()

    return {
        "users_total": users_total,
        "reservations_total": reservations_total,
        "confirmed_total": confirmed_total,
        "active_tables": active_tables,
        "reservation_statuses": status_rows,
        "weekday_load": weekday_rows,
        "popular_tables": popular_tables,
    }


# ========== EVENTS (Афиша мероприятий) ==========

def get_all_events(only_active: bool = True) -> list[dict[str, Any]]:
    """Получить все мероприятия"""
    query = """
        SELECT id, event_date, title, event_type, description, 
               start_time, price, is_active, image_url, created_at
        FROM events
    """
    params = []

    if only_active:
        query += " WHERE is_active = 1"

    query += " ORDER BY event_date ASC, start_time ASC"

    return _fetch_all(query, tuple(params))


def get_upcoming_events() -> list[dict[str, Any]]:
    """Получить предстоящие мероприятия (от сегодняшней даты)"""
    return _fetch_all(
        """
        SELECT id, event_date, title, event_type, description, 
               start_time, price, is_active, image_url, created_at
        FROM events
        WHERE event_date >= CURDATE() AND is_active = 1
        ORDER BY event_date ASC, start_time ASC
        """
    )


def get_event_by_id(event_id: int) -> Optional[dict[str, Any]]:
    """Получить мероприятие по ID"""
    return _fetch_one(
        """
        SELECT id, event_date, title, event_type, description, 
               start_time, price, is_active, image_url, created_at
        FROM events
        WHERE id = %s
        """,
        (event_id,),
    )


def get_events_by_type(event_type: str) -> list[dict[str, Any]]:
    """Получить мероприятия по типу"""
    return _fetch_all(
        """
        SELECT id, event_date, title, event_type, description, 
               start_time, price, is_active, image_url, created_at
        FROM events
        WHERE event_type = %s AND is_active = 1
        ORDER BY event_date ASC, start_time ASC
        """,
        (event_type,),
    )


def get_events_by_month(year: int, month: int) -> list[dict[str, Any]]:
    """Получить мероприятия за конкретный месяц"""
    return _fetch_all(
        """
        SELECT id, event_date, title, event_type, description, 
               start_time, price, is_active, image_url, created_at
        FROM events
        WHERE YEAR(event_date) = %s AND MONTH(event_date) = %s AND is_active = 1
        ORDER BY event_date ASC, start_time ASC
        """,
        (year, month),
    )