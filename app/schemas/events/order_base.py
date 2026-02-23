from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"


class OrderCreate(BaseModel):
    order_id: str = Field(..., json_schema_extra={"example": "ORD-123456"})
    user_id: Optional[int] = None
    status: OrderStatus
    country: Optional[str] = None
    event_time: datetime

    model_config = ConfigDict(from_attributes=True)
