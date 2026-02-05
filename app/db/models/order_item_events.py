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
from sqlalchemy.orm import declarative_base
import uuid
import enum

Base = declarative_base()

class OrderItemEvent(Base):
    """Individual line items for an order."""
    __tablename__ = "order_item_events"

    event_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(String, nullable=False, index=True)
    product_id = Column(String, nullable=False)
    description = Column(String)
    quantity = Column(Integer, nullable=False)
    price_at_purchase = Column(Integer, nullable=False, comment="Price in cents/pence")
    event_time = Column(DateTime(timezone=True), nullable=False)