''' so this is the API built for this entire tool.
so what this does it it will route the respective http requests to respective tables in the DB.
so for example if we want to get the user behavior events we will hit the endpoint /user_behavior_events.
it will route the request to the respective table in the DB.
we will have 7 endpoints for each of the tables in the DB.
so we will have endpoints for user_behavior_events, cart_events, purchase_events, product_events, hourly_product_behavior_agg, daily_product_behavior_agg, and product_recommendations.

'''
from fastapi import FastAPI
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session


from app.db import get_db
from app.db.models.cart_events import CartEvent
from app.db.models.user_behavior_events import UserBehaviorEvent
from app.db.models.payment_events import PaymentEvent
from app.db.models.order_item_events import OrderItemEvent
from app.db.models.logistics_events import LogisticsEvent
from app.db.models.order_events import OrderEvent
from app.db.models.aggregates import HourlyProductBehaviorAggregate



### first end point for our first table
router = APIRouter(prefix="/events", tags=["Events"])

# 1️ User Behavior
@router.post("/user-behavior", status_code=status.HTTP_201_CREATED)
def create_user_behavior_event(
    payload: UserBehaviorEvent,
    db: Session = Depends(get_db),
):
    db.add(payload)
    db.commit()
    db.refresh(payload)
    return payload


# 2️ Cart
@router.post("/cart", status_code=status.HTTP_201_CREATED)
def create_cart_event(
    payload: CartEvent,
    db: Session = Depends(get_db),
):
    db.add(payload)
    db.commit()
    db.refresh(payload)
    return payload


# 3️ Order
@router.post("/order", status_code=status.HTTP_201_CREATED)
def create_order_event(
    payload: OrderEvent,
    db: Session = Depends(get_db),
):
    db.add(payload)
    db.commit()
    db.refresh(payload)
    return payload


# 4️ Order Item
@router.post("/order-item", status_code=status.HTTP_201_CREATED)
def create_order_item_event(
    payload: OrderItemEvent,
    db: Session = Depends(get_db),
):
    db.add(payload)
    db.commit()
    db.refresh(payload)
    return payload


# 5️ Payment
@router.post("/payment", status_code=status.HTTP_201_CREATED)
def create_payment_event(
    payload: PaymentEvent,
    db: Session = Depends(get_db),
):
    db.add(payload)
    db.commit()
    db.refresh(payload)
    return payload


# 6️ Logistics
@router.post("/logistics", status_code=status.HTTP_201_CREATED)
def create_logistics_event(
    payload: LogisticsEvent,
    db: Session = Depends(get_db),
):
    db.add(payload)
    db.commit()
    db.refresh(payload)
    return payload


# 7️ GET User Behavior
@router.get("/user-behavior")
def get_user_behavior_events(db: Session = Depends(get_db)):
    return db.query(UserBehaviorEvent).limit(100).all()
