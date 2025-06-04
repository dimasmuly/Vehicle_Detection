#!/bin/bash

echo "=== Debugging Vehicle Counting Service ==="

# Stop existing services
echo "Stopping services..."
docker-compose down

# Clean up
echo "Cleaning up..."
docker system prune -f

# Start MediaMTX first
echo "Starting MediaMTX..."
docker-compose up -d mediamtx

# Wait for MediaMTX to be ready
echo "Waiting for MediaMTX to be ready..."
sleep 10

# Check MediaMTX status
echo "Checking MediaMTX API..."
curl -s http://localhost:9997/v3/paths/list || echo "MediaMTX API not ready"

# Start vehicle counting service
echo "Starting vehicle counting service..."
docker-compose up -d vehicle-counting

# Monitor logs
echo "\n=== MediaMTX Logs ==="
docker-compose logs --tail=10 mediamtx

echo "\n=== Vehicle Counting Logs ==="
docker-compose logs --tail=10 vehicle-counting

echo "\n=== Service Status ==="
docker-compose ps

echo "\n=== Real-time Monitoring ==="
echo "Run: docker-compose logs -f vehicle-counting"
echo "Or: docker-compose logs -f mediamtx"

echo "\n=== Stream URLs ==="
echo "HLS: http://localhost:8888/live/index.m3u8"
echo "RTSP: rtsp://localhost:8554/live"
echo "API: http://localhost:9997/v3/paths/list"