from fastapi.testclient import TestClient
from fastapi import status
import app.api.v1.dependencies.rate_limiter_dependency as rl_dep

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

