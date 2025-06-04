# Use official Python slim image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install build tools, cmake, git, python headers
RUN apt-get update && apt-get install -y \
    build-essential cmake git python3-dev \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get remove -y build-essential cmake git python3-dev \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*


# Copy only requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies without cache
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (adjust if needed)
EXPOSE 8000

# Run FastAPI app with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
