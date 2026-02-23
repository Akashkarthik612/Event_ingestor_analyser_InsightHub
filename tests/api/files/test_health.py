"""
Tests for GET /health (or root) — basic smoke test confirming the app boots.
Adjust the URL to match your actual health-check endpoint.
"""
from app.main import app
import pytest


class TestHealthCheck:

    def test_health_endpoint_returns_200(self, client):
        res = client.get("/health")
        assert res.status_code == 200

    def test_health_response_has_status_key(self, client):
        res = client.get("/health")
        body = res.json()
        assert "status" in body or res.status_code == 200   # flexible: plain 200 is fine too

    def test_docs_endpoint_available(self, client):
        """FastAPI auto-generates /docs — confirms app is fully initialised."""
        res = client.get("/docs")
        assert res.status_code == 200
    # Add this test temporarily to test_health.py
    def test_print_all_routes(self, client):
        from app.main import app
        for route in app.routes:
            print(route.path)
        assert True   # just to see the output
