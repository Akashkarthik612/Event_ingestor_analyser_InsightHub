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


class OrderResponse(OrderCreate):
    event_id: int

    model_config = ConfigDict(from_attributes=True)


class OrderItemCreate(BaseModel):
    order_id: str
    product_id: str
    description: Optional[str] = None
    quantity: int = Field(..., gt=0)
    price_at_purchase: int
    event_time: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderItemResponse(OrderItemCreate):
    event_id: int

    model_config = ConfigDict(from_attributes=True)