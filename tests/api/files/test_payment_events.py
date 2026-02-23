"""
Tests for POST /events/payment
Covers: Success / Refunded statuses, amount in cents, missing fields.
"""
import pytest

BASE_URL = "/api/v1/events/payment"


def make_payload(**overrides):
    base = {
        "order_id": "INV-PAY-001",
        "amount": 4999,          # £49.99 in pence
        "status": "Success",
        "event_time": "2024-06-01T10:00:00+00:00",
    }
    base.update(overrides)
    return base


class TestCreatePaymentEvent:

    def test_row1_successful_payment(self, client):
        payload = make_payload(order_id="INV-P-R1", amount=4999, status="Success")
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 201
        data = res.json()
        assert data["status"] == "Success"
        assert data["amount"] == 4999
        assert data["order_id"] == "INV-P-R1"
        assert "event_id" in data

    def test_row2_refunded_payment(self, client):
        payload = make_payload(order_id="INV-P-R2", amount=4999, status="Refunded")
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 201
        assert res.json()["status"] == "Refunded"

    def test_row3_large_amount(self, client):
        """High-value order: £9,999.99 → 999999 pence."""
        payload = make_payload(order_id="INV-P-R3", amount=999999, status="Success")
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 201
        assert res.json()["amount"] == 999999

    def test_row4_minimum_amount(self, client):
        payload = make_payload(order_id="INV-P-R4", amount=1, status="Success")
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 201
        assert res.json()["amount"] == 1

    def test_row5_failed_payment_status(self, client):
        """'Failed' is a plausible status string even if not an enum — should store as-is."""
        payload = make_payload(order_id="INV-P-R5", amount=2000, status="Failed")
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 201
        assert res.json()["status"] == "Failed"

    def test_row6_different_event_time_timezone(self, client):
        payload = make_payload(
            order_id="INV-P-R6",
            amount=1500,
            status="Success",
            event_time="2024-08-20T08:00:00+01:00",   # BST
        )
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 201
        assert res.json()["order_id"] == "INV-P-R6"

    def test_row7_multiple_payments_same_order(self, client):
        """An order can have multiple payment events (refund after success)."""
        p1 = make_payload(order_id="INV-P-R7", amount=5000, status="Success")
        p2 = make_payload(order_id="INV-P-R7", amount=5000, status="Refunded")
        r1 = client.post(BASE_URL, json=p1)
        r2 = client.post(BASE_URL, json=p2)
        assert r1.status_code == 201
        assert r2.status_code == 201
        assert r1.json()["event_id"] != r2.json()["event_id"]


class TestCreatePaymentEventValidation:

    def test_missing_order_id(self, client):
        payload = make_payload()
        del payload["order_id"]
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 422

    def test_missing_amount(self, client):
        payload = make_payload()
        del payload["amount"]
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 422

    def test_missing_status(self, client):
        payload = make_payload()
        del payload["status"]
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 422

    def test_missing_event_time(self, client):
        payload = make_payload()
        del payload["event_time"]
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 422

    def test_string_amount_rejected(self, client):
        payload = make_payload(amount="fifty-pounds")
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 422
