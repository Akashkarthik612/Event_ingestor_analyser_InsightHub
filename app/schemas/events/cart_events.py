from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional

class CartCreate(BaseModel):
    correlation_id: str
    user_id: Optional[int] = None
    product_id: int
    action: str  # 'add' or 'remove'
    quantity: int = Field(..., gt=0)
    event_time: datetime

    model_config = ConfigDict(from_attributes=True)