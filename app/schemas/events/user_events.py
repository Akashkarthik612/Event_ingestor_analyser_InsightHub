from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from enum import Enum

# Mirror the Enum from your DB model for strict validation
class UserBehaviorEventType(str, Enum):
    PRODUCT_VIEWED = "product_viewed"
    PRODUCT_SEARCHED = "product_searched"

class UserBehaviorCreate(BaseModel):
    # We don't include event_id or ingested_at because the DB generates those
    event_type: UserBehaviorEventType
    user_id: Optional[int] = None  # Match your 'nullable=True' for guests
    event_time: datetime
    product_id: int
    session_id: str
    country: Optional[str] = None
    source: Optional[str] = None
    platform: str 

    # This allows Pydantic to work with SQLAlchemy objects if needed later
    model_config = ConfigDict(from_attributes=True)