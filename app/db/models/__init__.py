"""
Import all models to register them with Base metadata.
This ensures they will be created when Base.metadata.create_all() is called.
"""
from app.db.models.user_behavior_events import UserBehaviorEvent, UserBehaviorEventType
from app.db.models.cart_events import CartEvent
from app.db.models.order_events import OrderEvent
from app.db.models.order_item_events import OrderItemEvent
from app.db.models.payment_events import PaymentEvent
from app.db.models.logistics_events import LogisticsEvent
from app.db.models.aggregates import HourlyProductBehaviorAggregate

__all__ = [
    "UserBehaviorEvent",
    "UserBehaviorEventType",
    "CartEvent",
    "OrderEvent",
    "OrderItemEvent",
    "PaymentEvent",
    "LogisticsEvent",
    "HourlyProductBehaviorAggregate",
]
