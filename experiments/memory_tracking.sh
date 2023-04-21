#!/bin/bash

# Get the folder path parameter
if [ -z "$1" ]; then
  echo "Folder path not provided"
  exit 1
fi
folder_path="$1"

# Run the memory tracking loop and save the output to the specified folder
while true; do
  free -m | awk 'NR==2{printf "%s,%s,%s,%s\n", strftime("%Y-%m-%d %H:%M:%S"), $2,$3,$4 }' >> "$folder_path/memory.log"
  sleep 10
done
