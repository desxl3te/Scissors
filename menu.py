"""Роуты для меню, бронирований, столиков и аналитики.

Часть атрибутов, нужных фронту, в исходной БД отсутствует.
Чтобы не вмешиваться в чужую схему, backend вычисляет такие поля на лету
в коде и не записывает их в MySQL.
"""

from datetime import datetime, timedelta
from decimal import Decimal
import hashlib
from typing import Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, Query, status

from database import get_connection
from dependencies import get_current_user, get_optional_current_user
from schemas import ReservationCreateRequest


router = APIRouter(prefix="/api", tags=["bar"])

# Эти метаданные нужны только для API-ответов.
# Важно: они больше не синхронизируются в БД и не требуют новых колонок.
PUBLIC_MENU_METADATA: Dict[str, Tuple[int, str, Optional[str]]] = {
    "Blessing wife": (22, "high", "images/cocktail-master.jpg"),
    "Third Wheel": (18, "medium", "images/hello-july.jpg"),
    "Send nudes": (26, "gay_panic", "images/summer-party.jpg"),
    "Pussy boy": (24, "high", "images/ladies-night.jpg"),
    "One Night Stand": (28, "gay_panic", "images/secret-party.jpg"),
    "Future Ex": (32, "medium", "напитки/future ex.jpg"),
    "Broken Vows": (35, "high", "напитки/broken vows.jpg"),
    "Bad Decision": (38, "gay_panic", "напитки/bad decision.jpg"),
    "Licked her": (30, "medium", "напитки/licked her.jpg"),
    "Сырная тарелка": (0, "soft", "images/food.png"),
    "Карпаччо из говядины": (0, "soft", "images/food.png"),
    "Креветки в темпуре": (0, "medium", "images/food.png"),
    "Брускетты с лососем": (0, "medium", "images/food.png"),
    "Острые крылышки": (0, "high", "images/food.png"),
    "Бургер \"Scissors\"": (0, "high", "images/food.png"),
    "Стейк Рибай": (0, "luxury", "images/food.png"),
    "Паста Карбонара": (0, "medium", "images/food.png"),
    "Ризотто с грибами": (0, "soft", "images/food.png"),
    "Салат с ростбифом": (0, "medium", "images/food.png"),
}

SECRET_MENU_METADATA: Dict[str, Tuple[int, str, Optional[str]]] = {
    "The Deer Penis": (42, "gay_panic", "напитки/the deer penis.jpg"),
}

TABLE_ZONE_MAPPING: Dict[int, str] = {
    1: "У окна",
    2: "У бара",
    3: "Темный угол",
    4: "У окна",
    5: "У бара",
}

ALLOWED_SORT_FIELDS: Dict[str, str] = {
    "name": "name",
    "price": "price",
    "strength": "strength",
    "drama_level": "drama_level",
    "category": "category",
}


def _serialize_datetime(value) -> Optional[str]:
    """Приводит datetime к стабильной строке."""

    if value is None:
        return None

    if isinstance(value, datetime):
        return value.replace(microsecond=0).isoformat(sep=" ")

    return str(value)


def _price_to_float(value) -> float:
    """Преобразует Decimal/число MySQL к float для JSON-ответа."""

    if isinstance(value, Decimal):
        return float(value)

    return float(value or 0)


def _get_public_menu_metadata(item_name: str) -> Tuple[int, str, Optional[str]]:
    """Возвращает служебные метаданные публичного меню по имени позиции."""

    return PUBLIC_MENU_METADATA.get(item_name, (0, "medium", None))


def _get_secret_menu_metadata(item_name: str) -> Tuple[int, str, Optional[str]]:
    """Возвращает служебные метаданные секретного меню по имени позиции."""

    return SECRET_MENU_METADATA.get(item_name, (0, "high", None))


def _table_zone_name(table_number: int) -> str:
    """Определяет зону столика в коде, без записи в БД."""

    return TABLE_ZONE_MAPPING.get(table_number, "Общий зал")


def _public_menu_item_to_dict(row: Dict[str, object]) -> Dict[str, object]:
    """Сериализует позицию основного меню.

    Дополнительные поля берём не из БД, а из словаря метаданных в коде.
    Это позволяет не менять исходную схему проекта.
    """

    strength, drama_level, image_path = _get_public_menu_metadata(row["name"])

    return {
        "id": row["id"],
        "name": row["name"],
        "category": row["category"],
        "price": _price_to_float(row["price"]),
        "description": row["description"],
        "strength": strength,
        "drama_level": drama_level,
        "is_secret": False,
        "available": bool(row["available"]),
        "image_path": image_path,
    }


def _secret_menu_item_to_dict(row: Dict[str, object]) -> Dict[str, object]:
    """Сериализует позицию секретного меню.

    В исходной таблице `secret_menu` нет признака активности, поэтому
    любая строка из неё считается доступной, если она существует.
    """

    strength, drama_level, image_path = _get_secret_menu_metadata(row["name"])

    return {
        "id": row["id"],
        "name": row["name"],
        "category": row["category"],
        "price": _price_to_float(row["price"]),
        "description": row["description"],
        "strength": strength,
        "drama_level": drama_level,
        "is_secret": True,
        "available": True,
        "image_path": image_path,
        "unlock_trigger": row["unlock_trigger"],
    }


def _table_to_dict(row: Dict[str, object], is_available: Optional[bool] = None) -> Dict[str, object]:
    """Сериализует столик для ответа API."""

    payload = {
        "id": row["id"],
        "table_number": row["table_number"],
        "seats_count": row["seats_count"],
        "zone_name": _table_zone_name(row["table_number"]),
        "is_active": bool(row["is_active"]),
    }

    if is_available is not None:
        payload["is_available"] = is_available

    return payload


def _serialize_user_brief(user: Dict[str, object]) -> Dict[str, object]:
    """Оставляет только краткую информацию о пользователе."""

    return {
        "id": user["id"],
        "user_name": user["user_name"],
        "email": user["email"],
    }


def _normalize_datetime(value: datetime) -> datetime:
    """Убирает микросекунды ради единообразия хранения и сравнения."""

    return value.replace(microsecond=0)


def _sort_menu_items(
    items: List[Dict[str, object]],
    sort_by: str,
    order: str,
) -> List[Dict[str, object]]:
    """Сортирует меню по полю, которое может быть как из БД, так и вычисляемым."""

    reverse = order.lower() == "desc"

    def sort_key(item: Dict[str, object]):
        value = item[sort_by]
        if isinstance(value, str):
            return (value.casefold(), item["id"])
        return (value, item["id"])

    return sorted(items, key=sort_key, reverse=reverse)


def _load_table_or_404(table_id: int) -> Dict[str, object]:
    """Загружает столик или выбрасывает 404."""

    with get_connection() as connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id, table_number, seats_count, is_active
            FROM tables
            WHERE id = %s
            """,
            (table_id,),
        )
        row = cursor.fetchone()
        cursor.close()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Столик не найден.",
        )

    return row


def _list_table_reservations(table_id: int) -> List[Tuple[datetime, datetime]]:
    """Возвращает подтверждённые брони столика как временные интервалы."""

    with get_connection() as connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT reservation_time, duration_hours
            FROM reservations
            WHERE table_id = %s AND status = 'confirmed'
            """,
            (table_id,),
        )
        rows = cursor.fetchall()
        cursor.close()

    intervals: List[Tuple[datetime, datetime]] = []

    for row in rows:
        start = _normalize_datetime(row["reservation_time"])
        end = start + timedelta(hours=row["duration_hours"])
        intervals.append((start, end))

    return intervals


def _ranges_overlap(
    left_start: datetime,
    left_end: datetime,
    right_start: datetime,
    right_end: datetime,
) -> bool:
    """Проверяет пересечение двух временных интервалов."""

    return left_start < right_end and right_start < left_end


def _is_table_available(
    table_id: int,
    reservation_time: datetime,
    duration_hours: int,
) -> bool:
    """Проверяет доступность столика в заданный интервал."""

    requested_start = _normalize_datetime(reservation_time)
    requested_end = requested_start + timedelta(hours=duration_hours)

    for existing_start, existing_end in _list_table_reservations(table_id):
        if _ranges_overlap(requested_start, requested_end, existing_start, existing_end):
            return False

    return True


@router.get("/menu")
def get_menu(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    category: Optional[str] = Query(None),
    drama_level: Optional[str] = Query(None),
    min_strength: Optional[int] = Query(None, ge=0, le=100),
    max_strength: Optional[int] = Query(None, ge=0, le=100),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    search: Optional[str] = Query(None),
    sort_by: str = Query("price"),
    order: str = Query("asc", pattern="^(asc|desc)$"),
) -> Dict[str, object]:
    """Возвращает основное меню с фильтрацией и пагинацией.

    Базовые фильтры применяем в SQL, а фильтры по вычисляемым полям
    (`strength`, `drama_level`) применяем уже в Python.
    """

    safe_sort = ALLOWED_SORT_FIELDS.get(sort_by, "price")
    where_clauses = ["available = 1"]
    params: List[object] = []

    if category:
        where_clauses.append("category = %s")
        params.append(category)

    if min_price is not None:
        where_clauses.append("price >= %s")
        params.append(min_price)

    if max_price is not None:
        where_clauses.append("price <= %s")
        params.append(max_price)

    if search and search.strip():
        where_clauses.append("(name LIKE %s OR description LIKE %s)")
        like_value = f"%{search.strip()}%"
        params.extend([like_value, like_value])

    where_sql = " AND ".join(where_clauses)
    offset = (page - 1) * limit

    with get_connection() as connection:
        data_cursor = connection.cursor(dictionary=True)
        data_cursor.execute(
            f"""
            SELECT id, name, category, price, description, available
            FROM menu_items
            WHERE {where_sql}
            """,
            params,
        )
        rows = data_cursor.fetchall()
        data_cursor.close()

    items = [_public_menu_item_to_dict(row) for row in rows]

    if drama_level:
        items = [item for item in items if item["drama_level"] == drama_level]

    if min_strength is not None:
        items = [item for item in items if item["strength"] >= min_strength]

    if max_strength is not None:
        items = [item for item in items if item["strength"] <= max_strength]

    total = len(items)
    items = _sort_menu_items(items, safe_sort, order)
    page_items = items[offset : offset + limit]

    return {
        "request": "menu",
        "data": page_items,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit if total else 0,
        },
        "filters": {
            "category": category,
            "drama_level": drama_level,
            "min_strength": min_strength,
            "max_strength": max_strength,
            "min_price": min_price,
            "max_price": max_price,
            "search": search,
            "sort_by": safe_sort,
            "order": order.lower(),
        },
    }


@router.get("/menu/categories")
def get_menu_categories() -> Dict[str, object]:
    """Возвращает список категорий основного меню."""

    with get_connection() as connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT DISTINCT category
            FROM menu_items
            WHERE available = 1
            ORDER BY category ASC
            """
        )
        rows = cursor.fetchall()
        cursor.close()

    return {
        "request": "menu_categories",
        "result": [row["category"] for row in rows],
    }


@router.get("/menu/secret")
def get_secret_menu(current_user: Dict[str, object] = Depends(get_current_user)) -> Dict[str, object]:
    """Возвращает секретное меню только для авторизованных пользователей."""

    with get_connection() as connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id, name, category, price, description, unlock_trigger
            FROM secret_menu
            ORDER BY price ASC, id ASC
            """
        )
        rows = cursor.fetchall()
        cursor.close()

    return {
        "request": "secret_menu",
        "user": _serialize_user_brief(current_user),
        "data": [_secret_menu_item_to_dict(row) for row in rows],
    }


@router.get("/menu/{item_id}")
def get_menu_item(
    item_id: int,
    current_user: Optional[Dict[str, object]] = Depends(get_optional_current_user),
) -> Dict[str, object]:
    """Возвращает одну позицию меню.

    Сначала ищем обычное меню. Если ничего не нашли и пользователь авторизован,
    дополнительно проверяем секретное меню.
    """

    with get_connection() as connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id, name, category, price, description, available
            FROM menu_items
            WHERE id = %s
            """,
            (item_id,),
        )
        public_row = cursor.fetchone()

        if public_row:
            cursor.close()
            return {
                "request": "menu_item",
                "result": _public_menu_item_to_dict(public_row),
            }

        if current_user is not None:
            cursor.execute(
                """
                SELECT id, name, category, price, description, unlock_trigger
                FROM secret_menu
                WHERE id = %s
                """,
                (item_id,),
            )
            secret_row = cursor.fetchone()
            cursor.close()

            if secret_row:
                return {
                    "request": "menu_item",
                    "result": _secret_menu_item_to_dict(secret_row),
                }
        else:
            cursor.close()

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Позиция меню не найдена.",
    )


@router.get("/tables")
def get_tables() -> Dict[str, object]:
    """Возвращает список активных столиков."""

    with get_connection() as connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id, table_number, seats_count, is_active
            FROM tables
            WHERE is_active = 1
            ORDER BY table_number ASC
            """
        )
        rows = cursor.fetchall()
        cursor.close()

    return {
        "request": "tables",
        "data": [_table_to_dict(row) for row in rows],
    }


@router.get("/tables/availability")
def get_tables_availability(
    reservation_time: datetime = Query(...),
    duration_hours: int = Query(2, ge=1, le=4),
    guests_count: int = Query(1, ge=1, le=12),
) -> Dict[str, object]:
    """Показывает, какие столики свободны в выбранный интервал."""

    normalized_time = _normalize_datetime(reservation_time)

    with get_connection() as connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id, table_number, seats_count, is_active
            FROM tables
            WHERE is_active = 1 AND seats_count >= %s
            ORDER BY seats_count ASC, table_number ASC
            """,
            (guests_count,),
        )
        rows = cursor.fetchall()
        cursor.close()

    return {
        "request": "tables_availability",
        "reservation_time": _serialize_datetime(normalized_time),
        "duration_hours": duration_hours,
        "guests_count": guests_count,
        "data": [
            _table_to_dict(
                row,
                is_available=_is_table_available(row["id"], normalized_time, duration_hours),
            )
            for row in rows
        ],
    }


@router.post("/reservations", status_code=status.HTTP_201_CREATED)
def create_reservation(
    payload: ReservationCreateRequest,
    current_user: Dict[str, object] = Depends(get_current_user),
) -> Dict[str, object]:
    """Создаёт новую бронь столика."""

    reservation_time = _normalize_datetime(payload.reservation_time)

    if reservation_time <= datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя создать бронь в прошлом.",
        )

    table = _load_table_or_404(payload.table_id)

    if not table["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Этот столик сейчас недоступен.",
        )

    if payload.guests_count > table["seats_count"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Количество гостей превышает вместимость столика.",
        )

    if not _is_table_available(table["id"], reservation_time, payload.duration_hours):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Столик уже занят на выбранное время.",
        )

    with get_connection() as connection:
        insert_cursor = connection.cursor()
        insert_cursor.execute(
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
                table["id"],
                current_user["id"],
                reservation_time,
                payload.duration_hours,
                payload.guests_count,
                payload.special_request,
            ),
        )
        reservation_id = insert_cursor.lastrowid
        insert_cursor.close()

        cursor = connection.cursor(dictionary=True)
        cursor.execute(
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
        reservation = cursor.fetchone()
        cursor.close()

    return {
        "request": "create_reservation",
        "result": {
            "id": reservation["id"],
            "table_id": reservation["table_id"],
            "table_number": reservation["table_number"],
            "zone_name": _table_zone_name(reservation["table_number"]),
            "reservation_time": _serialize_datetime(reservation["reservation_time"]),
            "duration_hours": reservation["duration_hours"],
            "guests_count": reservation["guests_count"],
            "status": reservation["status"],
            "special_request": reservation["special_request"],
            # В исходной таблице `reservations` нет created_at, поэтому честно
            # возвращаем None вместо выдуманного значения.
            "created_at": None,
        },
    }


@router.get("/reservations/me")
def get_my_reservations(
    current_user: Dict[str, object] = Depends(get_current_user),
) -> Dict[str, object]:
    """Возвращает брони текущего пользователя."""

    with get_connection() as connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
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
            (current_user["id"],),
        )
        rows = cursor.fetchall()
        cursor.close()

    return {
        "request": "my_reservations",
        "user": _serialize_user_brief(current_user),
        "data": [
            {
                "id": row["id"],
                "table_id": row["table_id"],
                "table_number": row["table_number"],
                "zone_name": _table_zone_name(row["table_number"]),
                "reservation_time": _serialize_datetime(row["reservation_time"]),
                "duration_hours": row["duration_hours"],
                "guests_count": row["guests_count"],
                "status": row["status"],
                "special_request": row["special_request"],
                "created_at": None,
            }
            for row in rows
        ],
    }


@router.patch("/reservations/{reservation_id}/cancel")
def cancel_reservation(
    reservation_id: int,
    current_user: Dict[str, object] = Depends(get_current_user),
) -> Dict[str, object]:
    """Отменяет бронь текущего пользователя."""

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
        reservation = cursor.fetchone()

        if not reservation:
            cursor.close()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Бронь не найдена.",
            )

        if reservation["user_id"] != current_user["id"]:
            cursor.close()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нельзя отменить чужую бронь.",
            )

        if reservation["status"] == "cancelled":
            cursor.close()
            return {
                "request": "cancel_reservation",
                "message": "Бронь уже была отменена ранее.",
            }

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
        cursor.close()

    return {
        "request": "cancel_reservation",
        "message": "Бронь успешно отменена.",
    }


@router.get("/analytics/overview")
def get_analytics_overview() -> Dict[str, object]:
    """Возвращает компактную сводку по сущностям, которые реально есть в БД."""

    with get_connection() as connection:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT COUNT(*) AS total FROM users")
        total_users = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM menu_items WHERE available = 1")
        total_public_menu_items = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM secret_menu")
        total_secret_menu_items = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM reservations")
        total_reservations = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM reservations WHERE status = 'confirmed'")
        confirmed_reservations = cursor.fetchone()["total"]

        cursor.close()

    return {
        "request": "analytics_overview",
        "result": {
            "users": total_users,
            "public_menu_items": total_public_menu_items,
            "secret_menu_items": total_secret_menu_items,
            "reservations_total": total_reservations,
            "reservations_confirmed": confirmed_reservations,
            "generated_at": _serialize_datetime(datetime.now()),
        },
    }


@router.get("/analytics/drama-stats")
def get_drama_statistics() -> Dict[str, object]:
    """Строит статистику по уровням драмы без использования дополнительных колонок."""

    with get_connection() as connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id, name, price
            FROM menu_items
            WHERE available = 1
            """
        )
        rows = cursor.fetchall()
        cursor.close()

    aggregates: Dict[str, Dict[str, float]] = {}

    for row in rows:
        strength, drama_level, _ = _get_public_menu_metadata(row["name"])
        bucket = aggregates.setdefault(
            drama_level,
            {
                "drama_level": drama_level,
                "drink_count": 0,
                "strength_sum": 0.0,
                "price_sum": 0.0,
            },
        )
        bucket["drink_count"] += 1
        bucket["strength_sum"] += float(strength)
        bucket["price_sum"] += _price_to_float(row["price"])

    result_rows = []
    for bucket in aggregates.values():
        drink_count = int(bucket["drink_count"])
        result_rows.append(
            {
                "drama_level": bucket["drama_level"],
                "drink_count": drink_count,
                "avg_strength": round(bucket["strength_sum"] / drink_count, 2) if drink_count else 0.0,
                "avg_price": round(bucket["price_sum"] / drink_count, 2) if drink_count else 0.0,
            }
        )

    result_rows.sort(key=lambda row: (-row["drink_count"], row["drama_level"]))

    return {
        "request": "drama_stats",
        "data": result_rows,
        "generated_at": _serialize_datetime(datetime.now()),
    }


@router.get("/hash/{str_input}")
def hash_string(str_input: str) -> Dict[str, object]:
    """Сервисная ручка для SHA-256 хеша строки."""

    return {
        "request": str_input,
        "result": hashlib.sha256(str_input.encode()).hexdigest(),
    }
