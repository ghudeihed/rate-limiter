import pytest
from fastapi.testclient import TestClient
from fastapi import status
from app.main import app

from app.api.v1.routes.resource import resource_router
from app.core.rate_limiter import RateLimiter
from app.api.v1.dependencies import rate_limiter_dependency
import app.api.v1.dependencies.rate_limiter_dependency as rl_dep

@pytest.fixture
def test_rate_limiter():
    return RateLimiter(rate=5, time_window=60)

@pytest.fixture(autouse=True)
def override_dependencies(test_rate_limiter):
    app.dependency_overrides[
        rate_limiter_dependency.get_rate_limiter_instance
    ] = lambda: test_rate_limiter

@pytest.fixture
def client():
    app.include_router(resource_router, prefix="/api/v1")
    with TestClient(app) as client:
        yield client
    app.dependency_overrides = {}

class TestRateLimiterEndpoint:
    def test_ping_allows_within_limit(self, client: TestClient):
        response = client.get("/api/v1/ping")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "pong"}

    def test_ping_rejects_exceeding_limit(self, client: TestClient):
        headers = {"X-Client-ID": "test-user"}
        for _ in range(5):
            client.get("/api/v1/ping", headers=headers)

        response = client.get("/api/v1/ping", headers=headers)
        assert response.status_code == 429
        assert "Rate limit exceeded" in response.json()["detail"]

    def test_ping_allows_in_new_window(self, client: TestClient, monkeypatch):
        headers = {"X-Client-ID": "test-user"}

        # Window 10s
        monkeypatch.setattr(rl_dep.time, "time", lambda: 10)
        for _ in range(5):
            client.get("/api/v1/ping", headers=headers)

        response = client.get("/api/v1/ping", headers=headers)
        assert response.status_code == 429

        # Window 70s
        monkeypatch.setattr(rl_dep.time, "time", lambda: 70)
        response = client.get("/api/v1/ping", headers=headers)
        assert response.status_code == 200

