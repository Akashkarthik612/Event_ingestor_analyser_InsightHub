"""
Tests for POST /events/cart
Covers: add/remove actions, nullable user_id (guest), missing required fields.
"""
import pytest

BASE_URL = "/events/cart"


def make_payload(**overrides):
    base = {
        "correlation_id": "sess-cart-001",
        "user_id": 101,
        "product_id": 2001,
        "action": "add",
        "quantity": 1,
        "event_time": "2024-06-01T10:00:00+00:00",
    }
    base.update(overrides)
    return base


class TestCreateCartEvent:

    def test_row1_add_action_authenticated_user(self, client):
        payload = make_payload(
            correlation_id="sess-c-row1",
            user_id=501,
            product_id=9001,
            action="add",
            quantity=2,
        )
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 201
        data = res.json()
        assert data["action"] == "add"
        assert data["quantity"] == 2
        assert data["user_id"] == 501
        assert "event_id" in data

    def test_row2_remove_action_authenticated_user(self, client):
        payload = make_payload(
            correlation_id="sess-c-row2",
            user_id=502,
            product_id=9002,
            action="remove",
            quantity=1,
        )
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 201
        assert res.json()["action"] == "remove"

    def test_row3_guest_user_null_user_id(self, client):
        payload = make_payload(
            correlation_id="sess-c-row3-guest",
            user_id=None,
            product_id=9003,
            action="add",
            quantity=3,
        )
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 201
        assert res.json()["user_id"] is None

    def test_row4_large_quantity(self, client):
        payload = make_payload(
            correlation_id="sess-c-row4",
            user_id=504,
            product_id=9004,
            action="add",
            quantity=999,
        )
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 201
        assert res.json()["quantity"] == 999

    def test_row5_different_timezone(self, client):
        payload = make_payload(
            correlation_id="sess-c-row5",
            user_id=505,
            product_id=9005,
            action="add",
            quantity=1,
            event_time="2024-07-04T12:00:00-05:00",
        )
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 201
        assert res.json()["product_id"] == 9005

    def test_row6_minimum_quantity_one(self, client):
        payload = make_payload(
            correlation_id="sess-c-row6",
            user_id=506,
            product_id=9006,
            action="add",
            quantity=1,
        )
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 201


class TestCreateCartEventValidation:

    def test_missing_correlation_id(self, client):
        payload = make_payload()
        del payload["correlation_id"]
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 422

    def test_missing_product_id(self, client):
        payload = make_payload()
        del payload["product_id"]
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 422

    def test_missing_action(self, client):
        payload = make_payload()
        del payload["action"]
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 422

    def test_missing_quantity(self, client):
        payload = make_payload()
        del payload["quantity"]
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 422

    def test_missing_event_time(self, client):
        payload = make_payload()
        del payload["event_time"]
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 422

    def test_invalid_event_time_format(self, client):
        payload = make_payload(event_time="yesterday")
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 422
