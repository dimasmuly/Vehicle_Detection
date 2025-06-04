FROM python:3.10-slim

# Install system dependencies including curl and wget
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libopencv-dev \
    python3-opencv \
    wget \
    curl \
    unzip \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY config/ ./config/
COPY videos/ ./videos/

# Make scripts executable
RUN chmod +x scripts/*.sh

# Download models if not present
RUN ./scripts/download_models.sh

# Expose port for health check
EXPOSE 8080

# Set environment variables for OpenVINO CPU optimization
ENV OMP_NUM_THREADS=4
ENV KMP_AFFINITY=granularity=fine,compact,1,0
ENV KMP_BLOCKTIME=1
ENV KMP_SETTINGS=1

# Run the application
CMD ["python", "src/vehicle_counting.py"]