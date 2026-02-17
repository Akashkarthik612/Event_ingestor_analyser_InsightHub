from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    Index,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
import uuid

class CartEvent(Base):
    __tablename__ = "cart_events"

    event_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    correlation_id = Column(String, nullable=False, comment="Maps to session_id")
    user_id = Column(Integer, nullable=True)
    product_id = Column(Integer, nullable=False)
    action = Column(String, nullable=False)   # whether the user added or removed the product from the cart
    quantity = Column(Integer, nullable=False)
    event_time = Column(DateTime(timezone=True), nullable=False)
    
    __table_args__ = (
        Index("idx_cart_user_time", "user_id", "event_time"),
    )