# Installation Guide

## Quick Start

The beauty of using BlenderProc is that you **don't need to manually install Blender**! BlenderProc automatically downloads and manages Blender for you.

### Prerequisites

- Python 3.9 or higher
- pip package manager
- (Optional) CUDA-capable GPU for faster rendering

### Installation Steps

1. **Clone or download this repository**:
   ```bash
   cd /path/to/blender-synth
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install the package**:
   ```bash
   pip install -e .
   ```

   This will:
   - Install all dependencies including BlenderProc
   - BlenderProc will automatically download Blender on first use
   - Set up the `blender-synth` command-line tool

4. **Verify installation**:
   ```bash
   blender-synth --help
   ```

That's it! No complicated Blender installation needed.

## First Run

On the **first run**, BlenderProc will download Blender automatically. This happens once and may take a few minutes:

```bash
blender-synth generate --models ./models --output ./output --num-images 10
```

You'll see output like:
```
Downloading Blender 3.x...
Extracting Blender...
Initializing BlenderProc...
```

Subsequent runs will use the cached Blender installation and start immediately.

## Organizing Your 3D Models

Create a directory structure for your archaeological artifacts:

```
models/
├── pottery/
│   ├── pot_001.obj
│   ├── pot_002.glb
│   └── pot_003.obj
├── tools/
│   ├── tool_001.obj
│   ├── tool_002.obj
│   └── tool_003.glb
└── ornaments/
    ├── ornament_001.obj
    └── ornament_002.glb
```

**Supported formats**:
- OBJ (.obj)
- GLTF/GLB (.gltf, .glb)
- PLY (.ply)
- STL (.stl)
- FBX (.fbx)

Directory names (pottery, tools, ornaments) become class labels automatically.

## GPU Acceleration (Optional but Recommended)

For faster rendering with CUDA:

**Linux**:
```bash
# Ensure NVIDIA drivers and CUDA are installed
nvidia-smi  # Should show your GPU
```

**Windows**:
- Install NVIDIA GPU drivers
- CUDA will be used automatically if available

The configuration files default to GPU rendering. To force CPU rendering, edit your config:

```yaml
rendering:
  use_gpu: false
```

## Troubleshooting

### BlenderProc fails to download Blender

If you have network issues, you can manually download Blender and point BlenderProc to it:

```bash
export BLENDER_PATH=/path/to/blender
```

### Out of memory errors

Reduce rendering samples or resolution:

```yaml
rendering:
  samples: 32  # Lower from 128

camera:
  resolution: [1280, 720]  # Lower from 1920x1080
```

### Import errors

Make sure you've activated your virtual environment:

```bash
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

## Development Installation

For contributing to the project:

```bash
pip install -e ".[dev]"
```

This installs additional tools:
- pytest (testing)
- black (code formatting)
- mypy (type checking)
- flake8 (linting)

## Next Steps

- See [README.md](README.md) for usage examples
- Check [examples/](examples/) for Python scripts
- Review [configs/](configs/) for configuration templates
