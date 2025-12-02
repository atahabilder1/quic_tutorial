FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    iproute2 \
    iputils-ping \
    net-tools \
    tcpdump \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt cryptography

# Copy application files
COPY . .

# Generate certificates if not present
RUN python generate_certs.py || true

# Expose QUIC port (UDP)
EXPOSE 4433/udp

# Default command
CMD ["python", "migration_demo.py"]
