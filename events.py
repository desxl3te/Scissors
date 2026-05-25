from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

import app.db.repository as repository

# мероприятия бара
router = APIRouter(prefix="/api/events", tags=["events"])


def _serialize_event(event: dict) -> dict:
    """сериализация мероприятия для JSON ответа"""
    return {
        "id": event["id"],
        "title": event["title"],
        "event_type": event["event_type"],
        "description": event["description"],
        "event_date": event["event_date"].isoformat() if event.get("event_date") else None,
        "start_time": str(event["start_time"]) if event.get("start_time") else None,
        "price": float(event["price"]) if event.get("price") else 0,
        "is_active": bool(event.get("is_active", True)),
        "image_url": event.get("image_url"),
        "created_at": event["created_at"].isoformat() if event.get("created_at") else None,
    }

# список с фильтрацией (по дате, типу, году/месяцу)
@router.get("/")
def get_events(
        upcoming: bool = Query(False, description="Только предстоящие"),
        event_type: Optional[str] = Query(None, description="Фильтр по типу"),
        year: Optional[int] = Query(None, description="Год"),
        month: Optional[int] = Query(None, description="Месяц"),
) -> dict:
    """
    получить список мероприятий с фильтрацией.
    """
    # Приоритет фильтров
    if upcoming:
        events = repository.get_upcoming_events()
    elif event_type:
        events = repository.get_events_by_type(event_type)
    elif year and month:
        events = repository.get_events_by_month(year, month)
    else:
        events = repository.get_all_events()

    return {
        "count": len(events),
        "data": [_serialize_event(e) for e in events]
    }

# детали мероприятия
@router.get("/{event_id}")
def get_event(event_id: int) -> dict:
    """
    получить мероприятие по ID.
    """
    event = repository.get_event_by_id(event_id)

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Мероприятие с ID {event_id} не найдено"
        )

    return {"data": _serialize_event(event)}

# список типов мероприятий
@router.get("/types/list")
def get_event_types() -> dict:
    """
    получить список всех типов мероприятий.
    """
    events = repository.get_all_events()
    types = list(set(e["event_type"] for e in events))
    return {"types": types}
