# Use a small Python image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Add dependency metadata
COPY pyproject.toml ./

# Install Poetry (system wide - not into virtual env.) + install dependencies
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root

# Copy actual app code
COPY app ./app

# Start the FastAPI app using uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
