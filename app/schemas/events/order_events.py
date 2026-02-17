from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional

class OrderItemCreate(BaseModel):
    order_id: str
    product_id: str
    description: Optional[str] = None
    quantity: int = Field(..., gt=0)
    price_at_purchase: int
    event_time: datetime

    model_config = ConfigDict(from_attributes=True)