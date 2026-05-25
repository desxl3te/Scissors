from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

# Pydantic модели для бронирований
class ReservationCreateRequest(BaseModel):
    table_id: int = Field(..., ge=1)
    reservation_time: datetime
    duration_hours: int = Field(default=2, ge=1, le=4)
    guests_count: int = Field(..., ge=1, le=12)
    special_request: Optional[str] = Field(default=None, max_length=500)
