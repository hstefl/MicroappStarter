from fastapi import FastAPI

from app.api.routes import router as order_router

app = FastAPI(title="Order Service", version="1.0.0")

app.include_router(order_router, prefix="/orders", tags=["orders"])


@app.get("/")
def root():
    return {"message": "Order Service is running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}