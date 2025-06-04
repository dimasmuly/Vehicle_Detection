#!/bin/bash

echo "Starting Vehicle Counting Service with MediaMTX Streaming..."

# Build and start services
docker-compose down
docker-compose build --no-cache
docker-compose up -d

echo "Services started!"
echo "Stream URLs:"
echo "  RTSP: rtsp://localhost:8554/live"
echo "  HLS: http://localhost:8888/live/index.m3u8"
echo "  WebRTC: http://localhost:8889/live"
echo "  API: http://localhost:9997"

# Wait for services to be ready
sleep 10

# Check service status
echo "\nService Status:"
docker-compose ps

echo "\nTo view logs:"
echo "  docker-compose logs -f vehicle-counting"
echo "  docker-compose logs -f mediamtx"

echo "\nTo stop services:"
echo "  docker-compose down"