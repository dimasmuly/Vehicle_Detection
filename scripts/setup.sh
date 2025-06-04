#!/bin/bash

echo "Setting up Vehicle Counting System..."

# Create necessary directories
mkdir -p videos models config docs

# Check if video exists, if not, inform user
if [ ! -f "videos/test_video.mp4" ]; then
    if [ -f "videos/test_video.mp4" ]; then
        echo "Using existing test_video.mp4 as sample video..."
        cp videos/test_video.mp4 videos/sample_traffic.mp4
    else
        echo "No sample video found. Please add a video file to the videos/ directory."
        echo "You can rename your video to 'sample_traffic.mp4' or update the config to use a different filename."
    fi
else
    echo "Sample video already exists."
fi

# Make scripts executable
chmod +x scripts/*.sh

echo "Setup completed!"