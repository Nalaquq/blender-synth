#!/bin/bash
# Launcher script for blender-synth that ensures it runs through blenderproc

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate virtual environment if it exists
if [ -d "$SCRIPT_DIR/venv" ]; then
    source "$SCRIPT_DIR/venv/bin/activate"
fi

# Set up CUDA library paths for GPU support in WSL2/Linux
# Add WSL CUDA libraries if they exist
if [ -d "/usr/lib/wsl/lib" ]; then
    export LD_LIBRARY_PATH="/usr/lib/wsl/lib:${LD_LIBRARY_PATH}"
fi

# Add system CUDA libraries if they exist
if [ -d "/usr/local/cuda/lib64" ]; then
    export LD_LIBRARY_PATH="/usr/local/cuda/lib64:${LD_LIBRARY_PATH}"
fi

# Also check for versioned CUDA installations
for cuda_dir in /usr/local/cuda-*/targets/x86_64-linux/lib; do
    if [ -d "$cuda_dir" ]; then
        export LD_LIBRARY_PATH="$cuda_dir:${LD_LIBRARY_PATH}"
        break  # Use the first one found
    fi
done

# Run blender-synth through blenderproc
blenderproc run "$SCRIPT_DIR/blender_synth/__main__.py" "$@"
