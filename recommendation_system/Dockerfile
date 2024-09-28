FROM --platform=linux/amd64 python:3.11-slim-buster AS builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libhdf5-dev \
    libpq-dev \
    gcc \
    libhdf5-serial-dev \
    libhdf5-103 \
    zlib1g-dev \
    libjpeg-dev \
    liblapack-dev \
    libblas-dev \
    gfortran \
    libatlas-base-dev \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app

# Set environment variable for file path
ENV CONFIG_PATH=/app/app/conf/configurations.json

# Make port 5000 available to the world outside this container
EXPOSE 5000

ENTRYPOINT ["python", "-m", "app"]
