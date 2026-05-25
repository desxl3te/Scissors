from __future__ import annotations
# хранение сообщений поддержки в JSON файле
from datetime import datetime
from typing import Optional

from app.core.config import settings
from app.core.files import read_json, write_json

# сохранение сообщения
def create_support_message(
    name: str,
    email: str,
    message: str,
    user_id: Optional[int] = None,
) -> dict:
    items = read_json(settings.support_messages_path, [])
    next_id = max((item["id"] for item in items), default=0) + 1
    payload = {
        "id": next_id,
        "name": name.strip(),
        "email": email.strip().lower(),
        "message": message.strip(),
        "user_id": user_id,
        "created_at": datetime.now().replace(microsecond=0).isoformat(sep=" "),
    }
    items.append(payload)
    write_json(settings.support_messages_path, items)
    return payload

# подсчет сообщений
def support_messages_count() -> int:
    return len(read_json(settings.support_messages_path, []))
