
import uuid
from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    Index,
    func
)
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base

class HourlyProductBehaviorAggregate(Base):
    """
    Stores hourly aggregates derived from user_behavior_events.
    This table is optimized for fast reads (dashboards, analytics, ML).
    """
    __tablename__ = "hourly_product_behavior_agg"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    product_id = Column(Integer, nullable=False)

    # Start of the hour bucket (e.g. 2025-01-25 14:00:00)
    event_hour = Column(DateTime(timezone=True), nullable=False)

    view_count = Column(Integer, nullable=False, default=0)
    search_count = Column(Integer, nullable=False, default=0)

    total_events = Column(Integer, nullable=False, default=0)

    last_updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    __table_args__ = (
        Index("idx_hourly_product_time", "product_id", "event_hour", unique=True),
    )