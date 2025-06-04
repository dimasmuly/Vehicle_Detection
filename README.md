# Vehicle Counting with OpenVINO and MediaMTX Streaming

Real-time vehicle counting system using OpenVINO for CPU-optimized inference and MediaMTX for live streaming.

## Features

- 🚗 Real-time vehicle detection and counting
- 🖥️ CPU-optimized OpenVINO inference
- 📺 Live streaming via MediaMTX (RTSP/HLS/WebRTC)
- 🔄 Infinite video looping
- 🐳 Docker containerized deployment
- 🌐 Browser-accessible stream viewer
- 📊 Real-time metadata overlay

## Quick Start

### Prerequisites

- Docker and Docker Compose
- At least 4GB RAM
- Multi-core CPU (recommended)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Vehicle_Detection
```

2. Setup the environment:
```bash
./scripts/setup.sh
```

3. Download pre-trained models:
```bash
./scripts/download_models.sh
```

4. Add your test video:
   - Place your video file in the `videos/` directory
   - Rename it to `test_video.mp4` or update the `INPUT_VIDEO` environment variable in `docker-compose.yml`

### Running the Service

1. Start the service:
```bash
./scripts/run_service.sh
```

2. Access the stream:
   - Web Player: Open `web/player.html` in your browser
   - RTSP: `rtsp://localhost:18554/live`
   - HLS: `http://localhost:18888/live/index.m3u8`
   - WebRTC: `http://localhost:18889/live`

3. Stop the service:
```bash
docker-compose down
```

## Advanced Usage

### Debugging

To debug the service:
```bash
./scripts/debug_service.sh
```

This will:
- Stop existing services
- Clean up Docker resources
- Start MediaMTX first
- Start the vehicle counting service
- Display logs for troubleshooting

### Rebuilding the Service

To rebuild the service from scratch:
```bash
./scripts/rebuild_service.sh
```

This will:
- Stop existing services
- Remove existing Docker images
- Clear Docker build cache
- Rebuild and restart the services

## Configuration

### Main Configuration

Edit `config/config.json` to modify:
- Model configurations
- Pipeline settings
- Detection parameters

### Environment Variables

Modify in `docker-compose.yml`:
- `MEDIAMTX_URL`: Streaming destination URL
- `INPUT_VIDEO`: Path to input video file
- `MODEL_PATH`: Path to model directory
- `OMP_NUM_THREADS`: Number of threads for OpenVINO
- `STREAM_OUTPUT`: Enable/disable streaming

### MediaMTX Configuration

Edit `config/mediamtx.yml` to modify:
- Streaming protocols (RTSP, HLS, WebRTC)
- Port settings
- Stream quality parameters

## System Architecture

The system consists of:
1. **Vehicle Detection**: OpenVINO-optimized detection model
2. **Video Processing**: Frame-by-frame analysis with metadata overlay
3. **Streaming Server**: MediaMTX for multi-protocol streaming
4. **Web Interface**: Browser-based stream viewer

## Documentation

A video demonstration of the system is available in the repository as `Documentation.mov`.

## Troubleshooting

### Common Issues

1. **Stream not available**:
   - Check if the services are running with `docker-compose ps`
   - Verify MediaMTX is running with `curl http://localhost:19997/v3/paths/list`
   - Check logs with `docker-compose logs -f`

2. **Performance issues**:
   - Adjust `OMP_NUM_THREADS` in `docker-compose.yml`
   - Reduce video resolution in `src/config.py`
   - Check CPU usage with `docker stats`

3. **Model errors**:
   - Ensure models are downloaded correctly
   - Check model paths in `config/config.json`
   - Run `./scripts/download_models.sh` to re-download models

## License

[Add your license information here]

        
