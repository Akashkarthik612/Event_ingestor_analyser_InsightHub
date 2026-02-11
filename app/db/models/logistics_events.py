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



class LogisticsEvent(Base):
    """Tracks shipping updates."""
    __tablename__ = "logistics_events"

    event_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(String, nullable=False, index=True)
    status = Column(Enum, nullable=False)
    event_time = Column(DateTime(timezone=True), nullable=False)