"""
Tests for POST /events/order
Covers: all OrderStatus enum values, nullable user_id, missing fields.
"""
import pytest

BASE_URL = "/events/order"


def make_payload(**overrides):
    base = {
        "order_id": "INV-001",
        "user_id": 601,
        "status": "pending",
        "country": "US",
        "event_time": "2024-06-01T10:00:00+00:00",
    }
    base.update(overrides)
    return base


class TestCreateOrderEvent:

    def test_row1_status_pending(self, client):
        payload = make_payload(order_id="INV-O-001", status="pending", user_id=601, country="US")
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 201
        data = res.json()
        assert data["status"] == "pending"
        assert data["order_id"] == "INV-O-001"
        assert "event_id" in data

    def test_row2_status_confirmed(self, client):
        payload = make_payload(order_id="INV-O-002", status="confirmed", user_id=602, country="GB")
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 201
        assert res.json()["status"] == "confirmed"

    def test_row3_status_shipped(self, client):
        payload = make_payload(order_id="INV-O-003", status="shipped", user_id=603, country="DE")
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 201
        assert res.json()["status"] == "shipped"

    def test_row4_status_cancelled(self, client):
        payload = make_payload(order_id="INV-O-004", status="cancelled", user_id=604, country="FR")
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 201
        assert res.json()["status"] == "cancelled"

    def test_row5_guest_user_null_user_id(self, client):
        payload = make_payload(order_id="INV-O-005", user_id=None, country=None)
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 201
        assert res.json()["user_id"] is None
        assert res.json()["country"] is None

    def test_row6_unique_order_id_per_insert(self, client):
        """order_id has a unique constraint — each insert must use a different order_id."""
        p1 = make_payload(order_id="INV-O-006a", status="pending")
        p2 = make_payload(order_id="INV-O-006b", status="confirmed")
        r1 = client.post(BASE_URL, json=p1)
        r2 = client.post(BASE_URL, json=p2)
        assert r1.status_code == 201
        assert r2.status_code == 201

    def test_duplicate_order_id_returns_error(self, client):
        """Inserting the same order_id twice should violate the unique constraint."""
        payload = make_payload(order_id="INV-DUP-001")
        client.post(BASE_URL, json=payload)
        res = client.post(BASE_URL, json=payload)
        # unique violation → 500 (integrity error) or 409 depending on error handler
        assert res.status_code in (409, 500)


class TestCreateOrderEventValidation:

    def test_missing_order_id(self, client):
        payload = make_payload()
        del payload["order_id"]
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 422

    def test_missing_status(self, client):
        payload = make_payload(order_id="INV-VAL-001")
        del payload["status"]
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 422

    def test_invalid_status_enum(self, client):
        payload = make_payload(order_id="INV-VAL-002", status="delivered")  # not in OrderStatus
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 422

    def test_missing_event_time(self, client):
        payload = make_payload(order_id="INV-VAL-003")
        del payload["event_time"]
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 422
