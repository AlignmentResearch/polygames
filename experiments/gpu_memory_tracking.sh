#!/bin/bash

folder="$1"             # Folder to store the log file
log_file="$folder/gpu_log.txt"  # File to store the GPU usage log
interval=10              # Interval in seconds between each log entry

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

# Check if log file exists, if not, create it with a header
if [ ! -f "$log_file" ]; then
    echo "Timestamp, GPU Utilization (%), Memory Usage (MiB)" > "$log_file"
fi

# Function to get current timestamp
get_timestamp() {
    date +"%Y-%m-%d %H:%M:%S"
}

# Function to log GPU usage
log_gpu_usage() {
    timestamp=$(get_timestamp)
    gpu_utilization=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits)
    memory_usage=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits)
    echo "$timestamp, $gpu_utilization, $memory_usage" >> "$log_file"
}

# Continuously log GPU usage
while true; do
    log_gpu_usage
    sleep "$interval"
done

