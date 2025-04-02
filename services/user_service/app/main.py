from fastapi import FastAPI

from app.api.routes import router as user_router

# Create the FastAPI app instance
app = FastAPI(
    title="User Service",  # Display name in Swagger docs
    version="1.0.0"  # API version
)

# Include the user API routes under the /users prefix
app.include_router(user_router, prefix="/users", tags=["users"])


# Optional root endpoint to verify the service is alive
@app.get("/")
def root():
    return {"message": "User Service is running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}