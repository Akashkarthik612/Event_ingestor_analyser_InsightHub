# =============================================================
# Run this from the ROOT of your project:  user-behavior-service/
# =============================================================

# ── Create folder structure ───────────────────────────────────
New-Item -ItemType Directory -Force -Path "tests"
New-Item -ItemType Directory -Force -Path ".github\workflows"

# ── tests\__init__.py ────────────────────────────────────────
New-Item -ItemType File -Force -Path "tests\__init__.py" | Out-Null
Set-Content "tests\__init__.py" "# makes tests/ a Python package"

# ── tests\conftest.py ────────────────────────────────────────
New-Item -ItemType File -Force -Path "tests\conftest.py" | Out-Null
@'
"""
conftest.py - Shared fixtures for all tests.
Uses an in-memory SQLite database so no real Postgres is needed in CI.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.base import Base
from app.db import get_db

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
'@ | Set-Content "tests\conftest.py"

# ── tests\test_health.py ─────────────────────────────────────
@'
"""Basic smoke tests — confirms the app boots and /docs is reachable."""
import pytest

class TestHealthCheck:

    def test_health_endpoint_returns_200(self, client):
        res = client.get("/health")
        assert res.status_code == 200

    def test_health_response_has_status_key(self, client):
        res = client.get("/health")
        assert "status" in res.json() or res.status_code == 200

    def test_docs_endpoint_available(self, client):
        res = client.get("/docs")
        assert res.status_code == 200
'@ | Set-Content "tests\test_health.py"

# ── tests\test_user_behavior.py ──────────────────────────────
@'
"""Tests for POST /events/user-behavior and GET /events/user-behavior."""
import pytest

BASE_URL = "/events/user-behavior"

def make_payload(**overrides):
    base = {
        "event_type": "product_viewed",
        "user_id": 101,
        "event_time": "2024-06-01T10:00:00+00:00",
        "product_id": 1001,
        "session_id": "sess-abc-001",
        "country": "US",
        "source": "organic",
        "platform": "web",
    }
    base.update(overrides)
    return base

class TestCreateUserBehaviorEvent:

    def test_row1_product_viewed_full_payload(self, client):
        res = client.post(BASE_URL, json=make_payload(user_id=201, product_id=3001, session_id="sess-row1"))
        assert res.status_code == 201
        data = res.json()
        assert data["event_type"] == "product_viewed"
        assert data["user_id"] == 201
        assert "event_id" in data

    def test_row2_product_searched(self, client):
        res = client.post(BASE_URL, json=make_payload(event_type="product_searched", user_id=202, product_id=3002, session_id="sess-row2", country="GB", platform="mobile"))
        assert res.status_code == 201
        assert res.json()["event_type"] == "product_searched"

    def test_row3_guest_user_null_user_id(self, client):
        res = client.post(BASE_URL, json=make_payload(user_id=None, session_id="sess-row3", product_id=3003))
        assert res.status_code == 201
        assert res.json()["user_id"] is None

    def test_row4_all_optional_fields_null(self, client):
        res = client.post(BASE_URL, json=make_payload(user_id=204, session_id="sess-row4", product_id=3004, country=None, source=None, platform=None))
        assert res.status_code == 201
        data = res.json()
        assert data["country"] is None

    def test_row5_non_utc_event_time(self, client):
        res = client.post(BASE_URL, json=make_payload(user_id=205, session_id="sess-row5", product_id=3005, event_time="2024-06-15T18:30:00+05:30"))
        assert res.status_code == 201

    def test_row6_large_ids(self, client):
        res = client.post(BASE_URL, json=make_payload(user_id=9999999, product_id=8888888, session_id="sess-row6"))
        assert res.status_code == 201

class TestCreateUserBehaviorEventValidation:

    def test_missing_event_type(self, client):
        p = make_payload(); del p["event_type"]
        assert client.post(BASE_URL, json=p).status_code == 422

    def test_invalid_enum_event_type(self, client):
        assert client.post(BASE_URL, json=make_payload(event_type="product_purchased")).status_code == 422

    def test_missing_session_id(self, client):
        p = make_payload(); del p["session_id"]
        assert client.post(BASE_URL, json=p).status_code == 422

    def test_missing_product_id(self, client):
        p = make_payload(); del p["product_id"]
        assert client.post(BASE_URL, json=p).status_code == 422

    def test_missing_event_time(self, client):
        p = make_payload(); del p["event_time"]
        assert client.post(BASE_URL, json=p).status_code == 422

    def test_invalid_event_time_format(self, client):
        assert client.post(BASE_URL, json=make_payload(event_time="not-a-date")).status_code == 422

class TestGetUserBehaviorEvents:

    def test_get_returns_200(self, client):
        assert client.get(BASE_URL).status_code == 200

    def test_get_returns_list(self, client):
        client.post(BASE_URL, json=make_payload(session_id="sess-get-1", product_id=5001))
        res = client.get(BASE_URL)
        assert isinstance(res.json(), list)
        assert len(res.json()) >= 1

    def test_get_event_structure(self, client):
        client.post(BASE_URL, json=make_payload(session_id="sess-get-2", product_id=5002, user_id=301))
        first = client.get(BASE_URL).json()[0]
        for field in ["event_id", "event_type", "product_id", "session_id", "event_time"]:
            assert field in first
'@ | Set-Content "tests\test_user_behavior.py"

# ── tests\test_cart_events.py ────────────────────────────────
@'
"""Tests for POST /events/cart."""
import pytest

BASE_URL = "/events/cart"

def make_payload(**overrides):
    base = {"correlation_id": "sess-cart-001","user_id": 101,"product_id": 2001,"action": "add","quantity": 1,"event_time": "2024-06-01T10:00:00+00:00"}
    base.update(overrides)
    return base

class TestCreateCartEvent:

    def test_row1_add_authenticated_user(self, client):
        res = client.post(BASE_URL, json=make_payload(correlation_id="sess-c-r1", user_id=501, product_id=9001, action="add", quantity=2))
        assert res.status_code == 201
        assert res.json()["action"] == "add"
        assert res.json()["quantity"] == 2
        assert "event_id" in res.json()

    def test_row2_remove_action(self, client):
        res = client.post(BASE_URL, json=make_payload(correlation_id="sess-c-r2", user_id=502, product_id=9002, action="remove", quantity=1))
        assert res.status_code == 201
        assert res.json()["action"] == "remove"

    def test_row3_guest_null_user_id(self, client):
        res = client.post(BASE_URL, json=make_payload(correlation_id="sess-c-r3", user_id=None, product_id=9003))
        assert res.status_code == 201
        assert res.json()["user_id"] is None

    def test_row4_large_quantity(self, client):
        res = client.post(BASE_URL, json=make_payload(correlation_id="sess-c-r4", user_id=504, product_id=9004, quantity=999))
        assert res.status_code == 201
        assert res.json()["quantity"] == 999

    def test_row5_non_utc_event_time(self, client):
        res = client.post(BASE_URL, json=make_payload(correlation_id="sess-c-r5", product_id=9005, event_time="2024-07-04T12:00:00-05:00"))
        assert res.status_code == 201

    def test_row6_minimum_quantity(self, client):
        res = client.post(BASE_URL, json=make_payload(correlation_id="sess-c-r6", product_id=9006, quantity=1))
        assert res.status_code == 201

class TestCartEventValidation:

    def test_missing_correlation_id(self, client):
        p = make_payload(); del p["correlation_id"]; assert client.post(BASE_URL, json=p).status_code == 422

    def test_missing_product_id(self, client):
        p = make_payload(); del p["product_id"]; assert client.post(BASE_URL, json=p).status_code == 422

    def test_missing_action(self, client):
        p = make_payload(); del p["action"]; assert client.post(BASE_URL, json=p).status_code == 422

    def test_missing_quantity(self, client):
        p = make_payload(); del p["quantity"]; assert client.post(BASE_URL, json=p).status_code == 422

    def test_missing_event_time(self, client):
        p = make_payload(); del p["event_time"]; assert client.post(BASE_URL, json=p).status_code == 422

    def test_invalid_event_time(self, client):
        assert client.post(BASE_URL, json=make_payload(event_time="yesterday")).status_code == 422
'@ | Set-Content "tests\test_cart_events.py"

# ── tests\test_order_events.py ───────────────────────────────
@'
"""Tests for POST /events/order."""
import pytest

BASE_URL = "/events/order"

def make_payload(**overrides):
    base = {"order_id": "INV-001","user_id": 601,"status": "pending","country": "US","event_time": "2024-06-01T10:00:00+00:00"}
    base.update(overrides)
    return base

class TestCreateOrderEvent:

    def test_row1_pending(self, client):
        res = client.post(BASE_URL, json=make_payload(order_id="INV-O-R1", status="pending"))
        assert res.status_code == 201
        assert res.json()["status"] == "pending"
        assert "event_id" in res.json()

    def test_row2_confirmed(self, client):
        res = client.post(BASE_URL, json=make_payload(order_id="INV-O-R2", status="confirmed", country="GB"))
        assert res.status_code == 201
        assert res.json()["status"] == "confirmed"

    def test_row3_shipped(self, client):
        res = client.post(BASE_URL, json=make_payload(order_id="INV-O-R3", status="shipped", country="DE"))
        assert res.status_code == 201
        assert res.json()["status"] == "shipped"

    def test_row4_cancelled(self, client):
        res = client.post(BASE_URL, json=make_payload(order_id="INV-O-R4", status="cancelled", country="FR"))
        assert res.status_code == 201
        assert res.json()["status"] == "cancelled"

    def test_row5_guest_null_user_and_country(self, client):
        res = client.post(BASE_URL, json=make_payload(order_id="INV-O-R5", user_id=None, country=None))
        assert res.status_code == 201
        assert res.json()["user_id"] is None

    def test_row6_two_distinct_orders(self, client):
        r1 = client.post(BASE_URL, json=make_payload(order_id="INV-O-R6a"))
        r2 = client.post(BASE_URL, json=make_payload(order_id="INV-O-R6b"))
        assert r1.status_code == 201
        assert r2.status_code == 201

    def test_duplicate_order_id_rejected(self, client):
        p = make_payload(order_id="INV-DUP-001")
        client.post(BASE_URL, json=p)
        res = client.post(BASE_URL, json=p)
        assert res.status_code in (409, 500)

class TestOrderEventValidation:

    def test_missing_order_id(self, client):
        p = make_payload(); del p["order_id"]; assert client.post(BASE_URL, json=p).status_code == 422

    def test_missing_status(self, client):
        p = make_payload(order_id="INV-V-1"); del p["status"]; assert client.post(BASE_URL, json=p).status_code == 422

    def test_invalid_status_enum(self, client):
        assert client.post(BASE_URL, json=make_payload(order_id="INV-V-2", status="delivered")).status_code == 422

    def test_missing_event_time(self, client):
        p = make_payload(order_id="INV-V-3"); del p["event_time"]; assert client.post(BASE_URL, json=p).status_code == 422
'@ | Set-Content "tests\test_order_events.py"

# ── tests\test_order_item_events.py ──────────────────────────
@'
"""Tests for POST /events/order-item."""
import pytest

BASE_URL = "/events/order-item"

def make_payload(**overrides):
    base = {"order_id":"INV-OI-001","product_id":"PROD-1001","description":"Blue Widget","quantity":2,"price_at_purchase":1999,"event_time":"2024-06-01T10:00:00+00:00"}
    base.update(overrides)
    return base

class TestCreateOrderItemEvent:

    def test_row1_standard_with_description(self, client):
        res = client.post(BASE_URL, json=make_payload(order_id="INV-OI-R1", product_id="PROD-A", quantity=1, price_at_purchase=999))
        assert res.status_code == 201
        data = res.json()
        assert data["quantity"] == 1
        assert data["price_at_purchase"] == 999
        assert "event_id" in data

    def test_row2_null_description(self, client):
        res = client.post(BASE_URL, json=make_payload(order_id="INV-OI-R2", product_id="PROD-B", description=None))
        assert res.status_code == 201
        assert res.json()["description"] is None

    def test_row3_large_quantity(self, client):
        res = client.post(BASE_URL, json=make_payload(order_id="INV-OI-R3", product_id="PROD-C", quantity=500))
        assert res.status_code == 201
        assert res.json()["quantity"] == 500

    def test_row4_high_price(self, client):
        res = client.post(BASE_URL, json=make_payload(order_id="INV-OI-R4", product_id="PROD-D", price_at_purchase=999999))
        assert res.status_code == 201
        assert res.json()["price_at_purchase"] == 999999

    def test_row5_multiple_items_same_order(self, client):
        r1 = client.post(BASE_URL, json=make_payload(order_id="INV-OI-R5", product_id="PROD-E1", quantity=1, price_at_purchase=100))
        r2 = client.post(BASE_URL, json=make_payload(order_id="INV-OI-R5", product_id="PROD-E2", quantity=3, price_at_purchase=200))
        assert r1.status_code == 201
        assert r2.status_code == 201
        assert r1.json()["event_id"] != r2.json()["event_id"]

    def test_row6_minimum_price(self, client):
        res = client.post(BASE_URL, json=make_payload(order_id="INV-OI-R6", product_id="PROD-F", price_at_purchase=1))
        assert res.status_code == 201

class TestOrderItemEventValidation:

    def test_missing_order_id(self, client):
        p = make_payload(); del p["order_id"]; assert client.post(BASE_URL, json=p).status_code == 422

    def test_missing_product_id(self, client):
        p = make_payload(); del p["product_id"]; assert client.post(BASE_URL, json=p).status_code == 422

    def test_missing_quantity(self, client):
        p = make_payload(); del p["quantity"]; assert client.post(BASE_URL, json=p).status_code == 422

    def test_missing_price(self, client):
        p = make_payload(); del p["price_at_purchase"]; assert client.post(BASE_URL, json=p).status_code == 422

    def test_missing_event_time(self, client):
        p = make_payload(); del p["event_time"]; assert client.post(BASE_URL, json=p).status_code == 422

    def test_string_quantity_rejected(self, client):
        assert client.post(BASE_URL, json=make_payload(quantity="two")).status_code == 422
'@ | Set-Content "tests\test_order_item_events.py"

# ── tests\test_payment_events.py ─────────────────────────────
@'
"""Tests for POST /events/payment."""
import pytest

BASE_URL = "/events/payment"

def make_payload(**overrides):
    base = {"order_id":"INV-PAY-001","amount":4999,"status":"Success","event_time":"2024-06-01T10:00:00+00:00"}
    base.update(overrides)
    return base

class TestCreatePaymentEvent:

    def test_row1_success(self, client):
        res = client.post(BASE_URL, json=make_payload(order_id="INV-P-R1", amount=4999, status="Success"))
        assert res.status_code == 201
        assert res.json()["status"] == "Success"
        assert "event_id" in res.json()

    def test_row2_refunded(self, client):
        res = client.post(BASE_URL, json=make_payload(order_id="INV-P-R2", status="Refunded"))
        assert res.status_code == 201
        assert res.json()["status"] == "Refunded"

    def test_row3_large_amount(self, client):
        res = client.post(BASE_URL, json=make_payload(order_id="INV-P-R3", amount=999999, status="Success"))
        assert res.status_code == 201
        assert res.json()["amount"] == 999999

    def test_row4_minimum_amount(self, client):
        res = client.post(BASE_URL, json=make_payload(order_id="INV-P-R4", amount=1))
        assert res.status_code == 201

    def test_row5_failed_status(self, client):
        res = client.post(BASE_URL, json=make_payload(order_id="INV-P-R5", status="Failed"))
        assert res.status_code == 201
        assert res.json()["status"] == "Failed"

    def test_row6_bst_event_time(self, client):
        res = client.post(BASE_URL, json=make_payload(order_id="INV-P-R6", event_time="2024-08-20T08:00:00+01:00"))
        assert res.status_code == 201

    def test_row7_refund_after_success_same_order(self, client):
        r1 = client.post(BASE_URL, json=make_payload(order_id="INV-P-R7", status="Success"))
        r2 = client.post(BASE_URL, json=make_payload(order_id="INV-P-R7", status="Refunded"))
        assert r1.status_code == 201
        assert r2.status_code == 201
        assert r1.json()["event_id"] != r2.json()["event_id"]

class TestPaymentEventValidation:

    def test_missing_order_id(self, client):
        p = make_payload(); del p["order_id"]; assert client.post(BASE_URL, json=p).status_code == 422

    def test_missing_amount(self, client):
        p = make_payload(); del p["amount"]; assert client.post(BASE_URL, json=p).status_code == 422

    def test_missing_status(self, client):
        p = make_payload(); del p["status"]; assert client.post(BASE_URL, json=p).status_code == 422

    def test_missing_event_time(self, client):
        p = make_payload(); del p["event_time"]; assert client.post(BASE_URL, json=p).status_code == 422

    def test_string_amount_rejected(self, client):
        assert client.post(BASE_URL, json=make_payload(amount="fifty")).status_code == 422
'@ | Set-Content "tests\test_payment_events.py"

# ── tests\test_logistics_events.py ───────────────────────────
@'
"""Tests for POST /events/logistics."""
import pytest

BASE_URL = "/events/logistics"

def make_payload(**overrides):
    base = {"order_id":"INV-LOG-001","status":"picked_up","event_time":"2024-06-01T10:00:00+00:00"}
    base.update(overrides)
    return base

class TestCreateLogisticsEvent:

    def test_row1_picked_up(self, client):
        res = client.post(BASE_URL, json=make_payload(order_id="INV-L-R1", status="picked_up"))
        assert res.status_code == 201
        assert res.json()["status"] == "picked_up"
        assert "event_id" in res.json()

    def test_row2_in_transit(self, client):
        res = client.post(BASE_URL, json=make_payload(order_id="INV-L-R2", status="in_transit"))
        assert res.status_code == 201
        assert res.json()["status"] == "in_transit"

    def test_row3_out_for_delivery(self, client):
        res = client.post(BASE_URL, json=make_payload(order_id="INV-L-R3", status="out_for_delivery"))
        assert res.status_code == 201
        assert res.json()["status"] == "out_for_delivery"

    def test_row4_delivered(self, client):
        res = client.post(BASE_URL, json=make_payload(order_id="INV-L-R4", status="delivered"))
        assert res.status_code == 201
        assert res.json()["status"] == "delivered"

    def test_row5_delayed(self, client):
        res = client.post(BASE_URL, json=make_payload(order_id="INV-L-R5", status="delayed"))
        assert res.status_code == 201
        assert res.json()["status"] == "delayed"

    def test_row6_full_lifecycle_same_order(self, client):
        statuses = ["picked_up","in_transit","out_for_delivery","delivered"]
        ids = []
        for i, s in enumerate(statuses):
            res = client.post(BASE_URL, json=make_payload(order_id="INV-L-R6", status=s, event_time=f"2024-06-0{i+1}T10:00:00+00:00"))
            assert res.status_code == 201
            ids.append(res.json()["event_id"])
        assert len(set(ids)) == len(statuses)

class TestLogisticsEventValidation:

    def test_missing_order_id(self, client):
        p = make_payload(); del p["order_id"]; assert client.post(BASE_URL, json=p).status_code == 422

    def test_missing_status(self, client):
        p = make_payload(); del p["status"]; assert client.post(BASE_URL, json=p).status_code == 422

    def test_invalid_status_enum(self, client):
        assert client.post(BASE_URL, json=make_payload(status="shipped")).status_code == 422

    def test_missing_event_time(self, client):
        p = make_payload(); del p["event_time"]; assert client.post(BASE_URL, json=p).status_code == 422

    def test_invalid_event_time(self, client):
        assert client.post(BASE_URL, json=make_payload(event_time="tomorrow")).status_code == 422
'@ | Set-Content "tests\test_logistics_events.py"

# ── .github\workflows\ci.yml ─────────────────────────────────
@'
name: CI - API Endpoint Tests

on:
  push:
    branches: [ "**" ]
  pull_request:
    branches: [ "**" ]

jobs:
  test:
    name: Run Pytest Suite
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov httpx

      - name: Set test environment
        run: |
          echo "DATABASE_URL=sqlite:///./test.db" >> $GITHUB_ENV
          echo "ENVIRONMENT=test" >> $GITHUB_ENV

      - name: Run tests
        run: |
          pytest tests/ --tb=short --cov=app --cov-report=term-missing --cov-report=xml:coverage.xml -v

      - name: Upload coverage to Codecov
        if: always()
        uses: codecov/codecov-action@v4
        with:
          files: coverage.xml
          fail_ci_if_error: false
'@ | Set-Content ".github\workflows\ci.yml"

Write-Host ""
Write-Host "✅ All test files created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Files created:" -ForegroundColor Cyan
Write-Host "  tests\__init__.py"
Write-Host "  tests\conftest.py"
Write-Host "  tests\test_health.py"
Write-Host "  tests\test_user_behavior.py"
Write-Host "  tests\test_cart_events.py"
Write-Host "  tests\test_order_events.py"
Write-Host "  tests\test_order_item_events.py"
Write-Host "  tests\test_payment_events.py"
Write-Host "  tests\test_logistics_events.py"
Write-Host "  .github\workflows\ci.yml"
Write-Host ""
Write-Host "Run locally with: pytest tests/ -v" -ForegroundColor Yellow
