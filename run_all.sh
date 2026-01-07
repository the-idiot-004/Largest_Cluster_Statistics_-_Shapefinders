#!/bin/bash
# This script runs the entire analysis pipeline.

# Ensure the script is run from the project root directory
if [ ! -f "main.py" ]; then
    echo "Error: This script must be run from the project root directory."
    exit 1
fi

# Run the main analysis script
python3 main.py