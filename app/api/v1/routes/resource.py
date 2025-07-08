from fastapi import APIRouter, Depends
from app.api.v1.dependencies.rate_limiter_dependency import get_rate_limiter

resource_router = APIRouter()

@resource_router.get("/ping")
def ping(rate_limited: bool = Depends(get_rate_limiter)):
    return {"message": "pong"}
