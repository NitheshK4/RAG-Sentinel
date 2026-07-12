"""
Tests for rate limiter, readiness probe, request-ID middleware,
system info endpoint, and incident detail/notes endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def _clear_incidents(client):
    """Ensure incident store is empty before each test."""
    client.delete("/api/v1/demo/incidents")
    yield
    client.delete("/api/v1/demo/incidents")


# ── Request-ID Middleware ──────────────────────────────────────────

class TestRequestIdMiddleware:
    def test_response_includes_request_id_header(self, client):
        """Every response should have an X-Request-Id header."""
        res = client.get("/api/v1/health")
        assert "x-request-id" in res.headers
        assert len(res.headers["x-request-id"]) > 0

    def test_client_request_id_is_propagated(self, client):
        """If the client sends X-Request-Id, the server should echo it back."""
        custom_id = "test-correlation-id-12345"
        res = client.get("/api/v1/health", headers={"X-Request-Id": custom_id})
        assert res.headers["x-request-id"] == custom_id

    def test_auto_generated_id_is_uuid_format(self, client):
        """Auto-generated IDs should be valid UUID4 strings."""
        import uuid
        res = client.get("/api/v1/health")
        request_id = res.headers["x-request-id"]
        # Should not raise — valid UUID
        uuid.UUID(request_id)


# ── Rate Limiter ───────────────────────────────────────────────────

class TestRateLimiter:
    def test_rate_limit_headers_present(self, client):
        """Responses should include rate-limit transparency headers."""
        res = client.get("/api/v1/demo/status")
        assert "x-ratelimit-limit" in res.headers
        assert "x-ratelimit-remaining" in res.headers

    def test_health_check_exempt_from_rate_limit(self, client):
        """Health endpoints should always work regardless of rate limits."""
        for _ in range(10):
            res = client.get("/api/v1/health")
            assert res.status_code == 200

    def test_rate_limit_values_decrease(self, client):
        """Verify that the remaining rate limit decreases sequentially across requests."""
        res1 = client.get("/api/v1/demo/status")
        rem1 = int(res1.headers["x-ratelimit-remaining"])
        
        res2 = client.get("/api/v1/demo/status")
        rem2 = int(res2.headers["x-ratelimit-remaining"])
        
        assert rem2 == rem1 - 1



# ── Readiness Endpoint ─────────────────────────────────────────────

class TestReadiness:
    def test_readiness_returns_200(self, client):
        """Readiness probe should return 200 in demo mode."""
        res = client.get("/api/v1/health/ready")
        assert res.status_code == 200
        data = res.json()
        assert data["ready"] is True
        assert "checks" in data

    def test_readiness_checks_all_components(self, client):
        """Readiness should check llm_api, incident_store, and settings_store."""
        res = client.get("/api/v1/health/ready")
        checks = res.json()["checks"]
        assert "llm_api" in checks
        assert "incident_store" in checks
        assert "settings_store" in checks

    def test_readiness_components_have_status(self, client):
        """Each component check should have status and detail fields."""
        res = client.get("/api/v1/health/ready")
        for name, check in res.json()["checks"].items():
            assert "status" in check, f"Missing 'status' in {name}"
            assert "detail" in check, f"Missing 'detail' in {name}"


# ── System Info ────────────────────────────────────────────────────

class TestSystemInfo:
    def test_system_info_returns_200(self, client):
        res = client.get("/api/v1/system/info")
        assert res.status_code == 200

    def test_system_info_has_app_section(self, client):
        data = client.get("/api/v1/system/info").json()
        assert "app" in data
        assert "title" in data["app"]
        assert "version" in data["app"]
        assert "demo_mode" in data["app"]
        assert "llm_model" in data["app"]

    def test_system_info_has_runtime_section(self, client):
        data = client.get("/api/v1/system/info").json()
        assert "runtime" in data
        assert "python_version" in data["runtime"]
        assert "platform" in data["runtime"]

    def test_system_info_has_dependencies(self, client):
        data = client.get("/api/v1/system/info").json()
        assert "dependencies" in data
        assert "fastapi" in data["dependencies"]
        assert "pydantic" in data["dependencies"]

    def test_system_info_has_route_count(self, client):
        data = client.get("/api/v1/system/info").json()
        assert "routes_registered" in data
        assert isinstance(data["routes_registered"], int)
        assert data["routes_registered"] > 0

    def test_system_info_dependency_versions(self, client):
        """Verify FastAPI and Pydantic versions are valid non-empty strings."""
        data = client.get("/api/v1/system/info").json()
        dependencies = data.get("dependencies", {})
        for name in ["fastapi", "pydantic"]:
            assert name in dependencies
            assert isinstance(dependencies[name], str)
            assert len(dependencies[name].strip()) > 0



# ── Incident Detail & Notes ───────────────────────────────────────

class TestIncidentDetail:
    def _seed_incident(self, client):
        client.post("/api/v1/demo/incidents", json={
            "stage": "chunk_audit",
            "data": {"chunk_id": "c_test", "severity": "high"},
            "ts": "2026-07-09T12:00:00Z"
        })

    def test_get_incident_by_index(self, client):
        self._seed_incident(client)
        res = client.get("/api/v1/demo/incidents/0")
        assert res.status_code == 200
        assert res.json()["stage"] == "chunk_audit"

    def test_get_incident_invalid_index_returns_404(self, client):
        res = client.get("/api/v1/demo/incidents/999")
        assert res.status_code == 404

    def test_add_note_to_incident(self, client):
        self._seed_incident(client)
        res = client.post("/api/v1/demo/incidents/0/notes", json={"note": "Confirmed false positive"})
        assert res.status_code == 200
        assert res.json()["notes_count"] == 1

    def test_add_multiple_notes(self, client):
        self._seed_incident(client)
        client.post("/api/v1/demo/incidents/0/notes", json={"note": "First note"})
        res = client.post("/api/v1/demo/incidents/0/notes", json={"note": "Second note"})
        assert res.json()["notes_count"] == 2

    def test_add_empty_note_returns_400(self, client):
        self._seed_incident(client)
        res = client.post("/api/v1/demo/incidents/0/notes", json={"note": ""})
        assert res.status_code == 400

    def test_add_note_invalid_index_returns_404(self, client):
        res = client.post("/api/v1/demo/incidents/999/notes", json={"note": "test"})
        assert res.status_code == 404

    def test_note_includes_timestamp(self, client):
        self._seed_incident(client)
        client.post("/api/v1/demo/incidents/0/notes", json={"note": "Timestamped note"})
        incident = client.get("/api/v1/demo/incidents/0").json()
        assert "analyst_notes" in incident
        assert "added_at" in incident["analyst_notes"][0]
