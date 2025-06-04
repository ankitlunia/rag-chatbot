FROM python:3.10-slim

WORKDIR /app

# Install build tools needed to compile llama-cpp-python
RUN apt-get update && apt-get install -y \
    build-essential cmake git python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies without cache
RUN pip install --no-cache-dir -r requirements.txt

# Remove build dependencies to reduce image size
RUN apt-get remove -y build-essential cmake git python3-dev \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Copy app code (model files excluded by .dockerignore)
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
