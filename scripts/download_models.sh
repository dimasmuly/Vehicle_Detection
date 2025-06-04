#!/bin/bash

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
MODELS_DIR="$PROJECT_DIR/models"

# Create models directory
echo "Creating models directory at: $MODELS_DIR"
mkdir -p "$MODELS_DIR"

# Check if models already exist
if [ -f "$MODELS_DIR/vehicle-detection-0202/1/vehicle-detection-0202.xml" ] && \
   [ -f "$MODELS_DIR/vehicle-detection-0202/1/vehicle-detection-0202.bin" ]; then
    echo "Vehicle detection model already exists, skipping download..."
else
    echo "Downloading vehicle detection model..."
    
    # Check for download tools
    if command -v wget >/dev/null 2>&1; then
        echo "Using wget for download..."
        wget -O "/tmp/vehicle-detection-0202.xml" "https://storage.openvinotoolkit.org/repositories/open_model_zoo/2022.1/models_bin/2/vehicle-detection-0202/FP32/vehicle-detection-0202.xml"
        wget -O "/tmp/vehicle-detection-0202.bin" "https://storage.openvinotoolkit.org/repositories/open_model_zoo/2022.1/models_bin/2/vehicle-detection-0202/FP32/vehicle-detection-0202.bin"
    elif command -v curl >/dev/null 2>&1; then
        echo "Using curl for download..."
        curl -L -o "/tmp/vehicle-detection-0202.xml" "https://storage.openvinotoolkit.org/repositories/open_model_zoo/2022.1/models_bin/2/vehicle-detection-0202/FP32/vehicle-detection-0202.xml"
        curl -L -o "/tmp/vehicle-detection-0202.bin" "https://storage.openvinotoolkit.org/repositories/open_model_zoo/2022.1/models_bin/2/vehicle-detection-0202/FP32/vehicle-detection-0202.bin"
    else
        echo "Error: Neither wget nor curl is available. Please install one of them."
        exit 1
    fi

    # Create model directory structure
    mkdir -p "$MODELS_DIR/vehicle-detection-0202/1"
    if [ -f "/tmp/vehicle-detection-0202.xml" ]; then
        mv "/tmp/vehicle-detection-0202.xml" "$MODELS_DIR/vehicle-detection-0202/1/"
        echo "✓ vehicle-detection-0202.xml downloaded successfully"
    else
        echo "✗ Error: vehicle-detection-0202.xml not found after download"
        exit 1
    fi

    if [ -f "/tmp/vehicle-detection-0202.bin" ]; then
        mv "/tmp/vehicle-detection-0202.bin" "$MODELS_DIR/vehicle-detection-0202/1/"
        echo "✓ vehicle-detection-0202.bin downloaded successfully"
    else
        echo "✗ Error: vehicle-detection-0202.bin not found after download"
        exit 1
    fi
fi

# Check if attributes model already exists
if [ -f "$MODELS_DIR/vehicle-attributes-recognition-barrier-0042/1/vehicle-attributes-recognition-barrier-0042.xml" ] && \
   [ -f "$MODELS_DIR/vehicle-attributes-recognition-barrier-0042/1/vehicle-attributes-recognition-barrier-0042.bin" ]; then
    echo "Vehicle attributes model already exists, skipping download..."
else
    echo "Downloading vehicle attributes recognition model..."
    
    if command -v wget >/dev/null 2>&1; then
        wget -O "/tmp/vehicle-attributes-recognition-barrier-0042.xml" "https://storage.openvinotoolkit.org/repositories/open_model_zoo/2022.1/models_bin/2/vehicle-attributes-recognition-barrier-0042/FP32/vehicle-attributes-recognition-barrier-0042.xml"
        wget -O "/tmp/vehicle-attributes-recognition-barrier-0042.bin" "https://storage.openvinotoolkit.org/repositories/open_model_zoo/2022.1/models_bin/2/vehicle-attributes-recognition-barrier-0042/FP32/vehicle-attributes-recognition-barrier-0042.bin"
    elif command -v curl >/dev/null 2>&1; then
        curl -L -o "/tmp/vehicle-attributes-recognition-barrier-0042.xml" "https://storage.openvinotoolkit.org/repositories/open_model_zoo/2022.1/models_bin/2/vehicle-attributes-recognition-barrier-0042/FP32/vehicle-attributes-recognition-barrier-0042.xml"
        curl -L -o "/tmp/vehicle-attributes-recognition-barrier-0042.bin" "https://storage.openvinotoolkit.org/repositories/open_model_zoo/2022.1/models_bin/2/vehicle-attributes-recognition-barrier-0042/FP32/vehicle-attributes-recognition-barrier-0042.bin"
    fi

    # Create model directory structure
    mkdir -p "$MODELS_DIR/vehicle-attributes-recognition-barrier-0042/1"
    if [ -f "/tmp/vehicle-attributes-recognition-barrier-0042.xml" ]; then
        mv "/tmp/vehicle-attributes-recognition-barrier-0042.xml" "$MODELS_DIR/vehicle-attributes-recognition-barrier-0042/1/"
        echo "✓ vehicle-attributes-recognition-barrier-0042.xml downloaded successfully"
    else
        echo "Warning: vehicle-attributes-recognition-barrier-0042.xml not found after download"
    fi

    if [ -f "/tmp/vehicle-attributes-recognition-barrier-0042.bin" ]; then
        mv "/tmp/vehicle-attributes-recognition-barrier-0042.bin" "$MODELS_DIR/vehicle-attributes-recognition-barrier-0042/1/"
        echo "✓ vehicle-attributes-recognition-barrier-0042.bin downloaded successfully"
    else
        echo "Warning: vehicle-attributes-recognition-barrier-0042.bin not found after download"
    fi
fi

echo "Model download completed!"
echo "Available models:"
ls -la "$MODELS_DIR/"*/1/