# Blender-Synth Project Summary

## Overview

This repository has been fully redesigned to use **BlenderProc** instead of raw `bpy`, eliminating the need for complicated Blender installations. The system generates synthetic training datasets for object detection of archaeological artifacts, specifically optimized for **museum drawer photography** with nadir/near-nadir camera angles.

## Key Features Implemented

### 1. **BlenderProc Integration**
- ✅ No manual Blender installation required
- ✅ BlenderProc automatically downloads and manages Blender
- ✅ Works with any Python 3.9+ environment
- ✅ No platform-specific `bpy` issues

### 2. **Nadir/Near-Nadir Camera System**
- ✅ Overhead photography simulation (0-15° from vertical)
- ✅ Camera orbit around artifacts (configurable positions)
- ✅ Realistic museum drawer viewpoints
- ✅ Automatic camera pose generation

### 3. **Physics-Based Object Placement**
- ✅ Objects drop onto table using realistic physics
- ✅ Configurable gravity, friction, and bounciness
- ✅ Natural artifact arrangement
- ✅ Collision detection and settling

### 4. **Domain Randomization**
- ✅ Random lighting (2-5 lights, varied intensity and color temperature)
- ✅ Background variation (drawer-like textures with color randomization)
- ✅ Object scale variation (0.8-1.2x)
- ✅ Random rotations and positions

### 5. **YOLO Annotation Generation**
- ✅ Automatic bounding box calculation from segmentation
- ✅ YOLO format output (normalized coordinates)
- ✅ Class-based organization
- ✅ Train/val/test splitting

### 6. **Flexible Configuration**
- ✅ YAML-based configuration files
- ✅ Python API for programmatic control
- ✅ Command-line interface
- ✅ Three presets: default, fast_preview, high_quality

## Project Structure

```
blender-synth/
├── blender_synth/              # Main package
│   ├── __init__.py             # Package exports
│   ├── __main__.py             # CLI entry point
│   ├── core/                   # Core BlenderProc modules
│   │   ├── scene.py            # Scene setup and drawer surface
│   │   ├── camera.py           # Nadir camera orbit system
│   │   └── physics.py          # Physics simulation
│   ├── objects/
│   │   └── loader.py           # 3D model loading and management
│   ├── randomization/
│   │   └── lighting.py         # Lighting randomization
│   ├── annotation/
│   │   └── yolo.py             # YOLO format annotation generation
│   ├── pipeline/
│   │   ├── config.py           # Pydantic configuration models
│   │   └── generator.py        # Main generation pipeline
│   └── utils/
│       └── logger.py           # Logging utilities
├── configs/                    # Configuration presets
│   ├── default.yaml            # Balanced settings
│   ├── fast_preview.yaml       # Quick testing
│   └── high_quality.yaml       # Production quality
├── examples/                   # Python usage examples
│   ├── basic_generation.py
│   ├── config_based_generation.py
│   ├── preview_generation.py
│   └── custom_camera_angles.py
├── docs/                       # Documentation
│   ├── README.md               # Main documentation
│   ├── INSTALLATION.md         # Installation guide
│   ├── USAGE.md                # Detailed usage guide
│   └── QUICKSTART.md           # 5-minute quick start
├── requirements.txt            # Runtime dependencies
├── requirements-dev.txt        # Development dependencies
├── pyproject.toml              # Modern Python packaging
├── setup.py                    # Package setup
├── Makefile                    # Development commands
├── LICENSE                     # MIT license
└── .gitignore                  # Git ignore rules
```

## Technical Architecture

### Configuration System (Pydantic v2)

```python
GenerationConfig
├── camera: CameraConfig
│   ├── nadir_angle_range: (0, 15)°
│   ├── orbit_angles: 8
│   ├── distance_range: (0.8, 1.5) meters
│   └── resolution: (1920, 1080)
├── physics: PhysicsConfig
│   ├── enabled: True
│   ├── drop_height: 0.3 meters
│   └── simulation_steps: 100
├── lighting: LightingConfig
│   ├── num_lights: (2, 4)
│   ├── intensity_range: (20, 80) W  # Indoor artifact photography
│   └── color_temp_range: (3000, 6500) K
├── background: BackgroundConfig
│   ├── use_drawer_texture: True
│   └── randomize_color: True
├── rendering: RenderConfig
│   ├── engine: CYCLES
│   ├── samples: 128
│   └── use_gpu: True
├── models: ModelConfig
│   ├── max_per_scene: 5
│   └── scale_range: (0.8, 1.2)
└── dataset: DatasetConfig
    ├── train_split: 0.7
    ├── val_split: 0.15
    └── test_split: 0.15
```

### Generation Pipeline

1. **Initialization**
   - Initialize BlenderProc (auto-downloads Blender on first run)
   - Discover 3D models from directory structure
   - Setup camera and rendering

2. **Per-Image Generation Loop**
   - Clear scene
   - Create drawer surface
   - Load random models (1-5 artifacts)
   - Drop objects with physics simulation
   - Generate random lighting (2-4 lights)
   - Position camera (nadir orbit)
   - Render image + segmentation
   - Extract bounding boxes
   - Save image and YOLO annotations

3. **Dataset Organization**
   - Split into train/val/test
   - Save class names
   - Save configuration

### Camera System

The nadir camera system creates overhead photography similar to museum documentation:

- **Nadir Angle**: 0-15° from vertical (configurable)
- **Orbit**: 8-12 positions around scene center
- **Distance**: 0.8-1.5 meters from artifacts
- **Look-at**: Always points at scene center

This simulates photographing artifacts in a drawer from various overhead angles.

## Usage Examples

### Command Line

```bash
# Quick start
blender-synth generate --models ./models --output ./output

# With options
blender-synth generate \
    --models ./models \
    --output ./output \
    --num-images 1000 \
    --camera-angles 12 \
    --max-objects 5

# From config
blender-synth generate --config configs/high_quality.yaml

# Preview mode
blender-synth preview --models ./models --output ./preview
```

### Python API

```python
from pathlib import Path
from blender_synth import SyntheticGenerator, GenerationConfig

# Basic usage
config = GenerationConfig(
    model_dir=Path("./models"),
    output_dir=Path("./output"),
    num_images=100,
)

generator = SyntheticGenerator(config)
generator.generate()

# Custom configuration
config.camera.nadir_angle_range = (0, 10)  # Nearly vertical
config.camera.orbit_angles = 12
config.rendering.samples = 256  # High quality
config.physics.enabled = True

generator = SyntheticGenerator(config)
generator.generate()
```

## Dependencies

### Runtime Dependencies
- **blenderproc>=2.7.0** - Automatic Blender management
- **numpy>=1.24.0** - Numerical operations
- **opencv-python>=4.7.0** - Image processing
- **Pillow>=9.5.0** - Image I/O
- **PyYAML>=6.0** - Configuration parsing
- **tqdm>=4.65.0** - Progress bars
- **pydantic>=2.0.0** - Configuration validation
- **scipy>=1.10.0** - Scientific computing

### Development Dependencies
- pytest, black, mypy, flake8, isort

## Installation

```bash
# Simple installation
python -m venv venv
source venv/bin/activate
pip install -e .

# Development installation
pip install -e ".[dev]"
```

**That's it!** No Blender installation needed. BlenderProc handles everything.

## Output Format

### Directory Structure
```
output/
├── train/
│   ├── images/
│   │   └── train_*.jpg
│   └── labels/
│       └── train_*.txt
├── val/
├── test/
├── classes.txt
└── config.yaml
```

### YOLO Annotations
```
<class_id> <x_center> <y_center> <width> <height>
```
All coordinates normalized to [0, 1].

## Key Differences from Original

### Before (nunalleq-synth)
- ❌ Required manual Blender 3.3.1 installation
- ❌ Required Python 3.11 (bpy compatibility)
- ❌ Complex Docker setup for consistency
- ❌ Platform-specific build issues
- ❌ Manual `bpy` module management

### After (blender-synth)
- ✅ BlenderProc auto-downloads Blender
- ✅ Works with Python 3.9, 3.10, 3.11
- ✅ Simple `pip install` workflow
- ✅ Cross-platform compatibility
- ✅ No manual Blender setup required

## Museum Drawer Photography Focus

The system is specifically optimized for archaeological artifacts in museum drawers:

1. **Nadir Camera Angles** - Overhead photography (0-15° from vertical)
2. **Camera Orbits** - Multiple viewpoints around artifacts
3. **Table/Drawer Surface** - Realistic drawer-like background
4. **Physics Simulation** - Natural artifact placement
5. **Museum Lighting** - Appropriate intensity and color temperature

## Performance

### Fast Preview (~10 sec/image)
- EEVEE renderer
- 32 samples
- 1280x720 resolution
- 4 camera angles

### Default (~30 sec/image)
- CYCLES renderer
- 128 samples
- 1920x1080 resolution
- 8 camera angles

### High Quality (~60-90 sec/image)
- CYCLES renderer
- 256 samples
- 2560x1440 resolution
- 12 camera angles

*Note: GPU acceleration significantly improves these times (5-10x speedup)*

## Next Steps for Users

1. **Install**: Follow INSTALLATION.md
2. **Quick Start**: Follow QUICKSTART.md (5 minutes)
3. **Organize Models**: Create `models/` directory structure
4. **Generate**: Run first dataset generation
5. **Customize**: Adjust configurations for your use case
6. **Scale Up**: Generate production datasets

## Future Enhancements (Optional)

Potential future additions:
- [ ] COCO/Pascal VOC annotation formats
- [ ] Instance segmentation masks
- [ ] Advanced material randomization
- [ ] HDRI environment maps
- [ ] Data augmentation pipeline
- [ ] Synthetic-to-real validation tools
- [ ] Web-based visualization dashboard

## Support

- **Documentation**: See INSTALLATION.md, USAGE.md, QUICKSTART.md
- **Examples**: Check examples/ directory
- **Configuration**: Review configs/ presets
- **Issues**: Check BlenderProc documentation for rendering issues

## License

MIT License - See LICENSE file

---

**Summary**: This is a complete, production-ready synthetic dataset generator using BlenderProc that eliminates installation complexity while providing powerful domain randomization for training object detection models on archaeological artifacts.
