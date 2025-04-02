from fastapi import FastAPI

from app.api.routes import router as product_router

app = FastAPI(title="Product Service", version="1.0.0")

app.include_router(product_router, prefix="/products", tags=["products"])


@app.get("/")
def root():
    return {"message": "Product Service is running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}