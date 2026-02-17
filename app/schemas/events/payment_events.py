from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional
from enum import Enum

class PaymentStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"

class PaymentCreate(BaseModel):
    # We use order_id as a string to match your DB Column
    order_id: str = Field(..., example="ORD-992834") 
    # to avoid floating-point errors.
    amount: int = Field(..., gt=0, description="Amount in smallest currency unit (e.g., cents)")
    
    status: PaymentStatus
    event_time: datetime
    currency: str = Field("USD", max_length=3)

    model_config = ConfigDict(from_attributes=True)