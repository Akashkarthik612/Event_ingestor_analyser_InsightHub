"""
Tests for POST /events/user-behavior  and  GET /events/user-behavior
Covers: valid inserts, enum validation, nullable fields, missing required fields.
"""
import pytest
from datetime import datetime, timezone


BASE_URL = "/api/v1/events/user-behavior"


# --------------------------------------------------------------------------- #
# Helper
# --------------------------------------------------------------------------- #
def make_payload(**overrides):
    """Return a minimal valid user-behavior payload, with optional overrides."""
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


# --------------------------------------------------------------------------- #
# POST — Happy-path (5 distinct rows)
# --------------------------------------------------------------------------- #
class TestCreateUserBehaviorEvent:

    def test_row1_product_viewed_full_payload(self, client):
        """Standard product_viewed event with all optional fields."""
        payload = make_payload(
            user_id=201,
            product_id=3001,
            session_id="sess-row1",
            country="US",
            source="organic",
            platform="web",
        )
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 201
        data = res.json()
        assert data["event_type"] == "product_viewed"
        assert data["user_id"] == 201
        assert data["product_id"] == 3001
        assert data["session_id"] == "sess-row1"
        assert data["country"] == "US"
        assert data["source"] == "organic"
        assert data["platform"] == "web"
        assert "event_id" in data

    def test_row2_product_searched_full_payload(self, client):
        """Standard product_searched event."""
        payload = make_payload(
            event_type="product_searched",
            user_id=202,
            product_id=3002,
            session_id="sess-row2",
            country="GB",
            source="paid",
            platform="mobile",
        )
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 201
        data = res.json()
        assert data["event_type"] == "product_searched"
        assert data["country"] == "GB"
        assert data["platform"] == "mobile"

    def test_row3_guest_user_null_user_id(self, client):
        """user_id is nullable — guest user scenario."""
        payload = make_payload(user_id=None, session_id="sess-row3-guest", product_id=3003)
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 201
        assert res.json()["user_id"] is None

    def test_row4_all_optional_fields_null(self, client):
        """country, source, platform are all nullable."""
        payload = make_payload(
            user_id=204,
            session_id="sess-row4",
            product_id=3004,
            country=None,
            source=None,
            platform=None,
        )
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 201
        data = res.json()
        assert data["country"] is None
        assert data["source"] is None
        assert data["platform"] is None

    def test_row5_different_timezone_event_time(self, client):
        """event_time with a non-UTC timezone offset should be accepted."""
        payload = make_payload(
            user_id=205,
            session_id="sess-row5",
            product_id=3005,
            event_time="2024-06-15T18:30:00+05:30",   # IST
        )
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 201
        assert res.json()["product_id"] == 3005

    def test_row6_large_product_id_and_user_id(self, client):
        """Boundary: very large integer IDs."""
        payload = make_payload(
            user_id=9_999_999,
            product_id=8_888_888,
            session_id="sess-row6-large",
        )
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 201
        assert res.json()["user_id"] == 9_999_999


# --------------------------------------------------------------------------- #
# POST — Validation / Error cases
# --------------------------------------------------------------------------- #
class TestCreateUserBehaviorEventValidation:

    def test_missing_required_event_type(self, client):
        payload = make_payload()
        del payload["event_type"]
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 422

    def test_invalid_enum_event_type(self, client):
        payload = make_payload(event_type="product_purchased")   # not in enum
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 422

    def test_missing_required_session_id(self, client):
        payload = make_payload()
        del payload["session_id"]
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 422

    def test_missing_required_product_id(self, client):
        payload = make_payload()
        del payload["product_id"]
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 422

    def test_missing_required_event_time(self, client):
        payload = make_payload()
        del payload["event_time"]
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 422

    def test_invalid_event_time_format(self, client):
        payload = make_payload(event_time="not-a-datetime")
        res = client.post(BASE_URL, json=payload)
        assert res.status_code == 422


# --------------------------------------------------------------------------- #
# GET /events/user-behavior
# --------------------------------------------------------------------------- #
class TestGetUserBehaviorEvents:

    def test_get_returns_200(self, client):
        res = client.get(BASE_URL)
        assert res.status_code == 200

    def test_get_returns_list(self, client):
        # seed one record first
        client.post(BASE_URL, json=make_payload(session_id="sess-get-1", product_id=5001))
        res = client.get(BASE_URL)
        assert isinstance(res.json(), list)
        assert len(res.json()) >= 1

    def test_get_event_structure(self, client):
        client.post(BASE_URL, json=make_payload(session_id="sess-get-2", product_id=5002, user_id=301))
        res = client.get(BASE_URL)
        first = res.json()[0]
        for field in ["event_id", "event_type", "product_id", "session_id", "event_time"]:
            assert field in first, f"Missing field: {field}"
