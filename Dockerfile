# Build stage
FROM python:3.10-slim AS build

WORKDIR /app

RUN apt-get update && apt-get install -y libgomp1 build-essential cmake git python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

COPY . .

# Final runtime stage
FROM python:3.10-slim

WORKDIR /app

# Copy installed packages from build stage
COPY --from=build /install /usr/local

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
