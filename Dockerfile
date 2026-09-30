# Base image
FROM python:3.10-slim-bookworm

# Set environment variables
ENV DockerHOME=/home/app/ \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies (will remove later)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    python3-dev \
    build-essential \
    && pip install --upgrade pip setuptools wheel

# Copy dependencies and install Python packages
COPY requirements.txt /app
RUN pip install -r requirements.txt

# Remove build dependencies to reduce image size
RUN apt-get remove --purge -y gcc python3-dev build-essential \
    && apt-get autoremove -y && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . /app

# Make the startup script executable
RUN chmod +x start-app.sh

# Expose the production port
EXPOSE 8000

# Run the start script
CMD ["./start-app.sh"]
