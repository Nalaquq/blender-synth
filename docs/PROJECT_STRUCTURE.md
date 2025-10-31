# Project Structure

This document describes the organization of the blender-synth project.

## Directory Overview

```
blender-synth/
├── blender_synth/          # Main package source code
├── configs/                # Configuration templates
├── docs/                   # Documentation
├── examples/               # Example usage scripts
├── models/                 # Input 3D models (user-provided, gitignored)
├── output/                 # Generated datasets (gitignored)
├── scripts/                # Utility and debug scripts
├── tests/                  # Test suite
└── [root files]            # Setup, requirements, README, etc.
```

## Detailed Structure

### `blender_synth/` - Main Package

The core package with all generation functionality:

```
blender_synth/
├── __init__.py             # Package initialization
├── __main__.py             # CLI entry point
├── annotation/             # Annotation generation
│   └── yolo.py            # YOLO format annotations
├── core/                   # Core rendering components
│   ├── camera.py          # Camera setup and positioning
│   ├── physics.py         # Physics simulation
│   └── scene.py           # Scene management and cleanup
├── objects/                # 3D model handling
│   └── loader.py          # Model loading and management
├── pipeline/               # Generation pipeline
│   ├── config.py          # Configuration classes (Pydantic models)
│   └── generator.py       # Main generation orchestration
├── randomization/          # Domain randomization
│   └── lighting.py        # Lighting randomization
├── utils/                  # Utility functions
│   ├── cuda_setup.py      # CUDA/OptiX detection
│   ├── gpu.py             # GPU configuration
│   └── logger.py          # Logging utilities
└── worker.py               # Worker processes (if needed)
```

### `configs/` - Configuration Templates

Pre-built configuration files for common scenarios:

```
configs/
├── default.yaml           # Default settings (recommended starting point)
├── fast_preview.yaml      # Quick preview with low quality
└── high_quality.yaml      # Maximum quality rendering
```

**Usage**: Copy and customize for your specific needs.

### `docs/` - Documentation

Comprehensive documentation for all aspects of the project:

```
docs/
├── index.md               # Documentation index and navigation
├── INSTALLATION.md        # Installation instructions
├── QUICKSTART.md          # 5-minute quick start guide
├── USAGE.md               # Complete usage documentation
├── GPU_SETUP.md           # GPU acceleration setup
├── LOGGING.md             # Logging system documentation
├── MEMORY_MONITORING.md   # Memory monitoring and optimization
├── PROJECT_SUMMARY.md     # Project architecture overview
├── PROJECT_STRUCTURE.md   # This file - project organization
└── CLEANUP_SUMMARY.md     # Recent refactoring notes
```

### `examples/` - Example Scripts

Python scripts demonstrating different use cases:

```
examples/
├── README.md                  # Examples documentation
├── basic_generation.py        # Simplest example
├── config_based_generation.py # Using YAML configs
├── preview_generation.py      # Fast preview generation
└── custom_camera_angles.py    # Custom camera setup
```

**Usage**: Copy examples to your own scripts and modify as needed.

### `models/` - Input 3D Models

User-provided 3D models organized by class:

```
models/                    # Not tracked in git
├── pottery/               # Class name = directory name
│   ├── pot_001.glb       # Supported: .glb, .gltf, .obj, .ply, .stl, .fbx
│   ├── pot_002.glb
│   └── ...
├── tools/
│   ├── tool_001.obj
│   └── ...
└── ornaments/
    └── ...
```

**Important**: Directory names become class labels automatically.

### `output/` - Generated Datasets

Output from generation runs:

```
output/                    # Not tracked in git
├── train/                 # Training split
│   ├── images/           # Generated images (.jpg)
│   └── labels/           # YOLO annotations (.txt)
├── val/                   # Validation split
│   ├── images/
│   └── labels/
├── test/                  # Test split
│   ├── images/
│   └── labels/
├── logs/                  # Detailed logs for each run
│   └── generation_YYYYMMDD_HHMMSS/
│       ├── generation.log          # Full text log
│       ├── memory_usage.csv        # Memory metrics
│       ├── generation_summary.json # Run statistics
│       └── run_metadata.json       # Configuration used
├── visualizations/        # Annotated preview images (optional)
│   ├── train/
│   ├── val/
│   └── test/
├── classes.txt            # Class names (one per line)
└── config.yaml            # Configuration used for generation
```

### `scripts/` - Utility Scripts

Helper scripts for development and production use:

```
scripts/
├── README.md              # Scripts documentation
├── utils/                 # Production utilities
│   ├── check_annotations.py      # Validate annotations
│   └── visualize_annotations.py  # Visualize bounding boxes
└── debug/                 # Development debugging
    ├── debug_camera_view.py
    ├── debug_segmentation.py
    └── ...
```

**Usage**:
- `utils/` scripts: Run with regular Python
- `debug/` scripts: Run with `blenderproc run`

### `tests/` - Test Suite

Test files for validating functionality:

```
tests/
├── README.md              # Test documentation
├── test_generation.py     # Main generation test
├── test_memory_fix.py     # Memory leak fix verification (100 images)
├── test_gpu_detection.py  # GPU detection tests
├── test_logging.py        # Logging system tests
└── ...
```

**Usage**: Run with `blenderproc run tests/test_name.py`

### Root Files

Configuration and setup files at the project root:

```
├── .gitignore             # Git ignore patterns
├── CHANGELOG.md           # Project changelog
├── CONTRIBUTING.md        # Contribution guidelines
├── LICENSE                # MIT license
├── Makefile               # Build automation
├── README.md              # Project overview (start here!)
├── pyproject.toml         # Python project metadata (PEP 517/518)
├── setup.py               # Package setup script
├── requirements.txt       # Production dependencies
├── requirements-dev.txt   # Development dependencies
└── run_blender_synth.sh   # Helper script for BlenderProc
```

## Key Files Explained

### Configuration Files

- **`pyproject.toml`** - Modern Python project metadata and build configuration
- **`setup.py`** - Package installation and distribution
- **`requirements.txt`** - Production dependencies (used by pip)
- **`requirements-dev.txt`** - Development dependencies (testing, linting, etc.)

### Entry Points

- **`blender_synth/__main__.py`** - CLI entry point (run with `python -m blender_synth` or `blender-synth`)
- **`blender_synth/__init__.py`** - Package API exports

### Helper Scripts

- **`run_blender_synth.sh`** - Wrapper for running scripts with BlenderProc
- **`test_memory_fix.py`** - Standalone test for memory leak fix

## Development Workflow

### Working with Source Code

1. **Core Functionality**: Modify files in `blender_synth/core/`
2. **Pipeline Changes**: Modify `blender_synth/pipeline/generator.py`
3. **New Features**: Add to appropriate subdirectory in `blender_synth/`
4. **Tests**: Add tests in `tests/` directory

### Working with Documentation

1. **User Docs**: Update files in `docs/`
2. **Examples**: Add scripts to `examples/`
3. **Main README**: Update `README.md` for overview changes
4. **Changelog**: Document changes in `CHANGELOG.md`

### Adding Utilities

1. **Production Tools**: Add to `scripts/utils/`
2. **Debug Tools**: Add to `scripts/debug/`
3. **Update**: Document in `scripts/README.md`

## Import Structure

When writing code, use these import patterns:

```python
# From the package
from blender_synth import SyntheticGenerator, GenerationConfig

# From submodules
from blender_synth.core.scene import SceneManager
from blender_synth.core.camera import CameraOrbit
from blender_synth.annotation.yolo import YOLOAnnotator

# From utils
from blender_synth.utils.logger import setup_logger
from blender_synth.utils.gpu import configure_gpu_rendering
```

## Output Organization

Generated datasets follow YOLO dataset format:

```
output/
├── train/images/           # Training images
├── train/labels/           # Training annotations
├── val/images/             # Validation images
├── val/labels/             # Validation annotations
├── test/images/            # Test images
├── test/labels/            # Test annotations
└── classes.txt             # Class name mapping
```

Each annotation file contains YOLO format lines:
```
<class_id> <x_center> <y_center> <width> <height>
```

All values except `class_id` are normalized to [0, 1].

## Memory Usage Monitoring

Generation runs produce detailed memory logs:

```
output/logs/generation_YYYYMMDD_HHMMSS/
├── generation.log          # Includes periodic memory logs
├── memory_usage.csv        # Detailed memory metrics
└── generation_summary.json # Peak memory statistics
```

See [Memory Monitoring](MEMORY_MONITORING.md) for details.

## See Also

- [Installation Guide](INSTALLATION.md) - Setup instructions
- [Usage Guide](USAGE.md) - How to use the tool
- [Project Summary](PROJECT_SUMMARY.md) - Architecture details
- [Contributing Guidelines](../CONTRIBUTING.md) - Development workflow
