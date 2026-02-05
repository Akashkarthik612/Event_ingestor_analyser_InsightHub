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

class CartEvent(Base):
    __tablename__ = "cart_events"

    event_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    correlation_id = Column(String, nullable=False, comment="Maps to session_id")
    user_id = Column(Integer, nullable=True)
    product_id = Column(Integer, nullable=False)
    action = Column(Enum(CartEventType), nullable=False)
    quantity = Column(Integer, nullable=False)
    event_time = Column(DateTime(timezone=True), nullable=False)
    
    __table_args__ = (
        Index("idx_cart_user_time", "user_id", "event_time"),
    )