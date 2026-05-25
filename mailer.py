from __future__ import annotations

import smtplib
from email.message import EmailMessage
from typing import Any

from app.core.config import settings

# отправка email через SMTP
def _smtp_configured() -> bool:
    """SMTP считается настроенным, только если заданы сервер, логин и пароль."""
    return bool(settings.smtp_host and settings.smtp_user and settings.smtp_password)

# отправка письма в поддержку
def send_support_email(item: dict[str, Any]) -> bool:
    """отправить сообщение поддержки на почтовый ящик.

    возвращает True при успешной отправке. любые ошибки гасятся внутри:
    сообщение уже сохранено в файл, поэтому сбой почты не должен ронять запрос.
    если SMTP не настроен в .env — просто возвращает False.
    """
    if not _smtp_configured():
        return False

    recipient = settings.support_inbox or settings.smtp_user
    sender = settings.smtp_from or settings.smtp_user

    message = EmailMessage()
    message["Subject"] = f"Поддержка Scissors Bar — сообщение #{item.get('id')}"
    message["From"] = sender
    message["To"] = recipient
    if item.get("email"):
        message["Reply-To"] = item["email"]

    message.set_content(
        "Новое сообщение из формы поддержки\n"
        "-----------------------------------\n"
        f"ID: {item.get('id')}\n"
        f"Имя: {item.get('name')}\n"
        f"Email отправителя: {item.get('email')}\n"
        f"User ID: {item.get('user_id')}\n"
        f"Дата: {item.get('created_at')}\n"
        "-----------------------------------\n\n"
        f"{item.get('message')}\n"
    )

    try:
        if settings.smtp_use_tls:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as server:
                server.starttls()
                server.login(settings.smtp_user, settings.smtp_password)
                server.send_message(message)
        else:
            with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, timeout=15) as server:
                server.login(settings.smtp_user, settings.smtp_password)
                server.send_message(message)
        return True
    except Exception as error:  # noqa: BLE001 - почта не должна ронять запрос
        print(f"[mailer] Не удалось отправить письмо поддержки: {error}")
        return False
