"""
Tests for POST /events/order-item
Covers: price in cents, nullable description, missing required fields.
"""
import pytest

BASE_URL = "/events/order-item"


def make_payload(**overrides):
    base = {
        "order_id": "INV-OI-001",
        "product_id": "PROD-1001",
        "description": "Blue Widget",
        "quantity": 2,
        "price_at_purchase": 1999,     # £19.99 in pence
        "event_time": "2024-06-01T10:00:00+00:00",
    }
    base.update(overrides)
    return base


class TestCreateOrderItemEvent:

    def test_row1_standard_item_with_description(self, client):
        payload = make_payload(
            order_id="INV-OI-R1",
            product_id="PROD-A",
            description="Red Widget",
            quantity=1,
            price_at_purchase=999,
        )
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 201
        data = res.json()
        assert data["order_id"] == "INV-OI-R1"
        assert data["product_id"] == "PROD-A"
        assert data["quantity"] == 1
        assert data["price_at_purchase"] == 999
        assert data["description"] == "Red Widget"
        assert "event_id" in data

    def test_row2_null_description(self, client):
        """description is nullable."""
        payload = make_payload(order_id="INV-OI-R2", product_id="PROD-B", description=None)
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 201
        assert res.json()["description"] is None

    def test_row3_large_quantity(self, client):
        payload = make_payload(order_id="INV-OI-R3", product_id="PROD-C", quantity=500, price_at_purchase=50)
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 201
        assert res.json()["quantity"] == 500

    def test_row4_high_price_luxury_item(self, client):
        """Price stored in cents/pence — £9,999.99 = 999999 pence."""
        payload = make_payload(order_id="INV-OI-R4", product_id="PROD-D", price_at_purchase=999999, quantity=1)
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 201
        assert res.json()["price_at_purchase"] == 999999

    def test_row5_multiple_items_same_order(self, client):
        """Same order_id can have multiple items (no unique constraint on order_item)."""
        p1 = make_payload(order_id="INV-OI-R5", product_id="PROD-E1", quantity=1, price_at_purchase=100)
        p2 = make_payload(order_id="INV-OI-R5", product_id="PROD-E2", quantity=3, price_at_purchase=200)
        r1 = client.post(BASE_URL, json=p1)
        r2 = client.post(BASE_URL, json=p2)
        assert r1.status_code == 201
        assert r2.status_code == 201
        # They must get different event_ids
        assert r1.json()["event_id"] != r2.json()["event_id"]

    def test_row6_minimum_price_one_cent(self, client):
        payload = make_payload(order_id="INV-OI-R6", product_id="PROD-F", price_at_purchase=1, quantity=1)
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 201
        assert res.json()["price_at_purchase"] == 1


class TestCreateOrderItemEventValidation:

    def test_missing_order_id(self, client):
        payload = make_payload()
        del payload["order_id"]
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 422

    def test_missing_product_id(self, client):
        payload = make_payload()
        del payload["product_id"]
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 422

    def test_missing_quantity(self, client):
        payload = make_payload()
        del payload["quantity"]
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 422

    def test_missing_price_at_purchase(self, client):
        payload = make_payload()
        del payload["price_at_purchase"]
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 422

    def test_missing_event_time(self, client):
        payload = make_payload()
        del payload["event_time"]
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 422

    def test_string_quantity_rejected(self, client):
        payload = make_payload(quantity="two")
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 422
