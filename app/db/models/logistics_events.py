from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    Enum,
    Index,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
import uuid
import enum


class LogisticsStatus(enum.Enum):
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    DELAYED = "delayed"


class LogisticsEvent(Base):
    """Tracks shipping updates."""
    __tablename__ = "logistics_events"

    event_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(String, nullable=False, index=True)
    status = Column(
        Enum(
            LogisticsStatus,
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            validate_strings=True,
        ),
        nullable=False,
    )
    event_time = Column(DateTime(timezone=True), nullable=False)
