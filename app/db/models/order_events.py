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


class OrderEvent(Base):
    """The 'Header' event for a transaction (Invoice level)."""
    __tablename__ = "order_events"

    event_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(String, nullable=False, unique=True, comment="Maps to InvoiceNo")
    user_id = Column(Integer, nullable=True)
    status = Column(Enum, nullable=False)
    country = Column(String)
    event_time = Column(DateTime(timezone=True), nullable=False)
    ingested_at = Column(DateTime(timezone=True), server_default=func.now())