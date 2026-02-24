from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class PaymentCreate(BaseModel):
    # We use order_id as a string to match your DB Column
    order_id: str = Field(..., json_schema_extra={"example": "ORD-992834"})
    # to avoid floating-point errors.
    amount: int = Field(..., gt=0, description="Amount in smallest currency unit (e.g., cents)")
    
    status: str
    event_time: datetime
    currency: str = Field("USD", max_length=3)

    model_config = ConfigDict(from_attributes=True)
