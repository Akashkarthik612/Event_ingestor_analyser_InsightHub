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



class PaymentEvent(Base):
    """Tracks payment status tied to an invoice."""
    __tablename__ = "payment_events"

    event_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(String, nullable=False, index=True)
    amount = Column(Integer, nullable=False)
    status = Column(String, nullable=False) # e.g., 'Success', 'Refunded'
    event_time = Column(DateTime(timezone=True), nullable=False)