"""
API Router for Event Ingestion

This router handles HTTP requests for various event types and routes them
to the appropriate database tables.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

# Import Pydantic schemas
from app.schemas.events.user_events import UserBehaviorCreate
from app.schemas.events.cart_events import CartCreate
from app.schemas.events.order_base import OrderCreate
from app.schemas.events.order_events import OrderItemCreate
from app.schemas.events.payment_events import PaymentCreate
from app.schemas.events.logistic_events import LogisticsCreate

# Import SQLAlchemy models
from app.db.models.user_behavior_events import UserBehaviorEvent
from app.db.models.cart_events import CartEvent
from app.db.models.order_events import OrderEvent
from app.db.models.order_item_events import OrderItemEvent
from app.db.models.payment_events import PaymentEvent
from app.db.models.logistics_events import LogisticsEvent

from app.db import get_db

router = APIRouter(prefix="/events", tags=["Events"])


# 1️ User Behavior
@router.post("/user-behavior", status_code=status.HTTP_201_CREATED)
def create_user_behavior_event(
    payload: UserBehaviorCreate,
    db: Session = Depends(get_db),
):
    """Create a new user behavior event."""
    db_event = UserBehaviorEvent(**payload.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


# 2️ Cart
@router.post("/cart", status_code=status.HTTP_201_CREATED)
def create_cart_event(
    payload: CartCreate,
    db: Session = Depends(get_db),
):
    """Create a new cart event."""
    db_event = CartEvent(**payload.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


# 3️ Order
@router.post("/order", status_code=status.HTTP_201_CREATED)
def create_order_event(
    payload: OrderCreate,
    db: Session = Depends(get_db),
):
    """Create a new order event."""
    db_event = OrderEvent(**payload.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


# 4️ Order Item
@router.post("/order-item", status_code=status.HTTP_201_CREATED)
def create_order_item_event(
    payload: OrderItemCreate,
    db: Session = Depends(get_db),
):
    """Create a new order item event."""
    db_event = OrderItemEvent(**payload.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


# 5️ Payment
@router.post("/payment", status_code=status.HTTP_201_CREATED)
def create_payment_event(
    payload: PaymentCreate,
    db: Session = Depends(get_db),
):
    """Create a new payment event."""
    db_event = PaymentEvent(**payload.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


# 6️ Logistics
@router.post("/logistics", status_code=status.HTTP_201_CREATED)
def create_logistics_event(
    payload: LogisticsCreate,
    db: Session = Depends(get_db),
):
    """Create a new logistics event."""
    db_event = LogisticsEvent(**payload.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


# GET endpoints
@router.get("/user-behavior")
def get_user_behavior_events(db: Session = Depends(get_db)):
    """Retrieve user behavior events (limited to 100)."""
    return db.query(UserBehaviorEvent).limit(100).all()
