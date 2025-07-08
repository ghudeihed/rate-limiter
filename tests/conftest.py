import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.v1.routes.resource import resource_router
from app.core.rate_limiter import RateLimiter
from app.api.v1.dependencies import rate_limiter_dependency

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
