#!/bin/bash

echo "Rebuilding Vehicle Counting Service..."

# Stop existing services
echo "Stopping existing services..."
docker-compose down

# Remove existing images to force rebuild
echo "Removing existing images..."
docker rmi vehicle_counting-vehicle-counting 2>/dev/null || true

# Clear Docker build cache
echo "Clearing Docker build cache..."
docker builder prune -f

# Build and start services with no cache
echo "Building services with no cache..."
docker-compose build --no-cache

echo "Starting services..."
docker-compose up -d

echo "Services restarted!"
echo "Stream URLs:"
echo "  RTSP: rtsp://localhost:8554/live"
echo "  HLS: http://localhost:8888/live/index.m3u8"
echo "  WebRTC: http://localhost:8889/live"
echo "  API: http://localhost:9997"

# Wait for services to be ready
sleep 15

# Check service status
echo "\nService Status:"
docker-compose ps

echo "\nChecking vehicle-counting logs:"
docker-compose logs --tail=20 vehicle-counting

echo "\nTo view real-time logs:"
echo "  docker-compose logs -f vehicle-counting"
echo "  docker-compose logs -f mediamtx"