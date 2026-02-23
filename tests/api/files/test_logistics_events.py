"""
Tests for POST /events/logistics
Covers: all 5 LogisticsStatus enum values, missing fields, bad enum.
"""
import pytest

BASE_URL = "/api/v1/events/logistics"


def make_payload(**overrides):
    base = {
        "order_id": "INV-LOG-001",
        "status": "picked_up",
        "event_time": "2024-06-01T10:00:00+00:00",
    }
    base.update(overrides)
    return base


class TestCreateLogisticsEvent:

    def test_row1_picked_up(self, client):
        payload = make_payload(order_id="INV-L-R1", status="picked_up")
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 201
        data = res.json()
        assert data["status"] == "picked_up"
        assert data["order_id"] == "INV-L-R1"
        assert "event_id" in data

    def test_row2_in_transit(self, client):
        payload = make_payload(order_id="INV-L-R2", status="in_transit")
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 201
        assert res.json()["status"] == "in_transit"

    def test_row3_out_for_delivery(self, client):
        payload = make_payload(order_id="INV-L-R3", status="out_for_delivery")
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 201
        assert res.json()["status"] == "out_for_delivery"

    def test_row4_delivered(self, client):
        payload = make_payload(order_id="INV-L-R4", status="delivered")
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 201
        assert res.json()["status"] == "delivered"

    def test_row5_delayed(self, client):
        payload = make_payload(order_id="INV-L-R5", status="delayed")
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 201
        assert res.json()["status"] == "delayed"

    def test_row6_full_lifecycle_same_order(self, client):
        """An order progresses through multiple logistics states."""
        statuses = ["picked_up", "in_transit", "out_for_delivery", "delivered"]
        event_ids = []
        for i, status in enumerate(statuses):
            payload = make_payload(
                order_id="INV-L-R6",
                status=status,
                event_time=f"2024-06-0{i+1}T10:00:00+00:00",
            )
            res = client.post(BASE_URL, json=payload)
            assert res.status_code == 201, f"Failed for status: {status}"
            event_ids.append(res.json()["event_id"])

        # All event_ids must be unique
        assert len(set(event_ids)) == len(statuses)


class TestCreateLogisticsEventValidation:

    def test_missing_order_id(self, client):
        payload = make_payload()
        del payload["order_id"]
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 422

    def test_missing_status(self, client):
        payload = make_payload()
        del payload["status"]
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 422

    def test_invalid_status_enum(self, client):
        """'shipped' is not a LogisticsStatus value."""
        payload = make_payload(status="shipped")
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 422

    def test_missing_event_time(self, client):
        payload = make_payload()
        del payload["event_time"]
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 422

    def test_invalid_event_time(self, client):
        payload = make_payload(event_time="tomorrow")
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 422