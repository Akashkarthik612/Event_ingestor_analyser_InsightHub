from pydantic import BaseModel, ConfigDict
from datetime import datetime
from enum import Enum

class LogisticsStatus(str, Enum):
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    DELAYED = "delayed"

class LogisticsCreate(BaseModel):
    order_id: str
    status: LogisticsStatus
    event_time: datetime

    model_config = ConfigDict(from_attributes=True)