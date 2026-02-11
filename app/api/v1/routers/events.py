''' so this is the API built for this entire tool.
so what this does it it will route the respective http requests to respective tables in the DB.
so for example if we want to get the user behavior events we will hit the endpoint /user_behavior_events.
it will route the request to the respective table in the DB.
we will have 7 endpoints for each of the tables in the DB.
so we will have endpoints for user_behavior_events, cart_events, purchase_events, product_events, hourly_product_behavior_agg, daily_product_behavior_agg, and product_recommendations.

'''
from fastapi import FastAPI
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session


from app.db import get_db
from app.db.models.cart_events import CartEvent
from app.db.models.user_behavior_events import UserBehaviorEvent
from app.db.models.payment_events import PaymentEvent
from app.db.models.order_item_events import OrderItemEvent
from app.db.models.logistics_events import LogisticsEvent
from app.db.models.order_events import OrderEvent
from app.db.models.aggregates import HourlyProductBehaviorAggregate


app = FastAPI()    ## the fast API is loaded in this app variable

### first end point for our first table
@app.get("/user_behavior_events")
async def get_user_behavior_events(db: Session = Depends(get_db)):
    ''' the main use of this endpoint is get the user behavior events from the DB and return it to the client.''''
    events_fetch = db.query(UserBehaviorEvent).all() ### this will fetch all the datas from the table as of now we will update and modify later
    
    
    return events_fetch
    
@app.get("/payments_events")

async def get_payments_events(db:Session = Depends(get_db)):
    events_fetch = db.query(PaymentEvent).all()
    
    return events_fetch
    
@app.get("/cart_events")
async def cart_payments(db: Session = Depends(get_db)):
    events_fetch = db.query(CartEvent).all()
    
    
    return events_fetch
    
@app.get("/order_events")
async def order_events(db: Session = Depends(get_db)):
    events_fetch = db.query(OrderEvent).all()
    
    
    return events_fetch   
    
@app.get("/logistics_events")
async def logistics_events(db: Session = Depends(get_db)):
    events_fetch = db.query(LogisticsEvent).all()
    
    
    return events_fetch 
    
@app.get("/order_item_events")
async def logistics_events(db: Session = Depends(get_db)):
    events_fetch = db.query(OrderItemEvent).all()
    
    
    return events_fetch 
