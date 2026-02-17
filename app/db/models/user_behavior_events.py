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

class UserBehaviorEventType(enum.Enum):
    PRODUCT_VIEWED = "product_viewed"
    PRODUCT_SEARCHED = "product_searched"
    
    
class UserBehaviorEvent(Base):
    __tablename__ = "user_behavior_events"
    
    ###primary key###
    event_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable = False) # this is unique for all the tables
    
    event_type = Column(Enum(UserBehaviorEventType), nullable=False)
    user_id = Column(Integer,
        nullable=True,
        comment="Nullable to support guest users",)
    event_time = Column(DateTime(timezone=True), nullable=False)
    ingested_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    product_id = Column(Integer, nullable=False)
    session_id = Column(String, nullable=False)
    country = Column(String, nullable=True)
    source = Column(String, nullable=True)
    
    __table_args__ = (
        Index("idx_user_behavior_user_time", "user_id", "event_time"),
        Index("idx_user_behavior_product_time", "product_id", "event_time"),
    )