#!/bin/bash

folder="$1"                 # Folder to store the log file
log_file="$folder/gpu_log.txt"  # File to store the GPU usage log
interval=5                  # Interval in seconds between each log entry

# Check if nvidia-smi is installed
if ! command -v nvidia-smi &> /dev/null; then
    echo "nvidia-smi command not found. Make sure you have NVIDIA drivers installed."
    exit 1
fi

# Check if folder exists, if not, create it
if [ ! -d "$folder" ]; then
    echo "Creating folder: $folder"
    mkdir -p "$folder"
fi

# Continuously append GPU usage to log file
while true; do
    nvidia-smi >> "$log_file"
    sleep "$interval"
done
