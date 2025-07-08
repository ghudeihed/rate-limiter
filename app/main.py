from fastapi import FastAPI
from app.api.v1.routes.resource import resource_router

app = FastAPI(title="Rate Limiter API")

# Include resource router
app.include_router(resource_router, prefix="/api/v1", tags=["resource"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Rate Limiter API!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
