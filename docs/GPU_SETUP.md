# GPU Support Setup Guide

This guide explains how to enable GPU acceleration for Blender rendering in WSL2/Linux environments.

## Quick Start

### Using the Shell Script (Recommended)

The `run_blender_synth.sh` script automatically sets up CUDA library paths:

```bash
./run_blender_synth.sh
```

The script automatically detects and adds CUDA libraries from:
- `/usr/lib/wsl/lib` (WSL2 NVIDIA driver passthrough)
- `/usr/local/cuda/lib64` (Standard CUDA installation)
- `/usr/local/cuda-*/` (Versioned CUDA installations)

### Using Python Scripts Directly

If you're running scripts directly with `blenderproc run`, add this at the **very top** of your script (before importing blenderproc):

```python
# IMPORTANT: Set up CUDA environment BEFORE importing blenderproc
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from blender_synth.utils.cuda_setup import setup_cuda_environment
setup_cuda_environment()

import blenderproc as bproc
# ... rest of your imports and code
```

### Manual Environment Setup

Alternatively, set the `LD_LIBRARY_PATH` environment variable before running blenderproc:

```bash
export LD_LIBRARY_PATH=/usr/lib/wsl/lib:/usr/local/cuda/lib64:$LD_LIBRARY_PATH
blenderproc run your_script.py
```

## Verifying GPU Support

When GPU is detected, you'll see messages like:

```
INFO - Detected 1 GPU device(s) using CUDA: NVIDIA RTX A4000 Laptop GPU (CUDA)
INFO - ============================================================
INFO - RENDERING MODE: GPU
INFO - ============================================================
INFO - Rendering with CYCLES engine using GPU
INFO - Device: GPU (NVIDIA RTX A4000 Laptop GPU (CUDA))
```

If GPU is not detected, you'll see:

```
INFO - No GPU devices detected for any compute device type
INFO - No GPU devices available - falling back to CPU rendering
INFO - ============================================================
INFO - RENDERING MODE: CPU
INFO - ============================================================
```

## Configuration

GPU usage can be controlled via the `RenderConfig`:

```python
from blender_synth import GenerationConfig

# Prefer GPU (default)
config = GenerationConfig(
    model_dir=Path("./models"),
    output_dir=Path("./output"),
)
config.rendering.use_gpu = True  # Default: automatically uses GPU if available

# Force CPU rendering
config.rendering.use_gpu = False
```

## Troubleshooting

### GPU Not Detected

1. **Check NVIDIA driver in WSL2:**
   ```bash
   nvidia-smi
   ```
   Should show your GPU.

2. **Check CUDA libraries exist:**
   ```bash
   ls /usr/lib/wsl/lib/libcuda*
   ls /usr/local/cuda*/lib64/
   ```

3. **Verify LD_LIBRARY_PATH:**
   ```bash
   echo $LD_LIBRARY_PATH
   ```
   Should include CUDA library paths.

4. **Test Blender GPU detection:**
   ```bash
   blenderproc run test_blender_gpu_info.py
   ```

### WSL2 Setup

Ensure you have:
1. Windows 11 or Windows 10 with WSL2
2. NVIDIA GPU drivers installed on Windows
3. WSL2 kernel with GPU support enabled

No CUDA installation needed inside WSL2 - it uses the Windows driver.

### Linux Setup

For native Linux:
1. Install NVIDIA drivers
2. Install CUDA Toolkit (matching your GPU):
   ```bash
   sudo apt install nvidia-cuda-toolkit
   ```

## Supported GPUs

- NVIDIA GPUs with CUDA support (Compute Capability 3.0+)
- For OptiX acceleration: NVIDIA RTX series (Turing+ architecture)

## Performance Notes

- **OptiX** (RTX GPUs): Fastest, uses hardware ray tracing
- **CUDA**: Fast, works on all CUDA-capable NVIDIA GPUs
- **CPU**: Slowest, but works everywhere

The code automatically selects the best available option in this order:
1. OptiX (if RTX GPU available)
2. CUDA (if NVIDIA GPU available)
3. CPU (fallback)
