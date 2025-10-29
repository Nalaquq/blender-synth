# Blender-Synth: Synthetic Dataset Generator for Archaeological Artifacts

A BlenderProc-based synthetic dataset generator for training object detection models on archaeological artifacts, specifically designed for museum drawer photography scenarios.

## Features

- **Simple Installation**: Uses BlenderProc - no complicated Blender setup required
- **Physics-Based Placement**: Realistic artifact positioning using physics simulation
- **Nadir/Near-Nadir Camera**: Simulates overhead museum drawer photography
- **Camera Orbit**: Multiple viewing angles around artifacts
- **Domain Randomization**: Varied lighting, materials, and backgrounds for robust training
- **YOLO Format**: Automatic annotation generation in YOLO format
- **Batch Processing**: Generate thousands of annotated images efficiently

## Use Case

This tool is designed for generating synthetic training data for detecting archaeological artifacts placed in museum drawers and photographed from above (nadir or near-nadir angles). Perfect for:

- Museum digitization projects
- Archaeological object detection
- Cultural heritage preservation
- Training computer vision models with limited real-world data

## Documentation

Full documentation is available in the [`docs/`](docs/) directory:

- **[Quick Start Guide](docs/QUICKSTART.md)** - Get started in minutes
- **[Installation Guide](docs/INSTALLATION.md)** - Detailed installation instructions
- **[GPU Setup](docs/GPU_SETUP.md)** - Configure GPU acceleration
- **[Usage Guide](docs/USAGE.md)** - Complete usage documentation
- **[Logging System](docs/LOGGING.md)** - Understanding logs and debugging
- **[Project Summary](docs/PROJECT_SUMMARY.md)** - Architecture and technical details

## Quick Installation

```bash
# Create virtual environment (Python 3.9+ recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install package
pip install -e .
```

BlenderProc will automatically download and manage Blender for you - no manual installation needed!

For detailed installation instructions including GPU setup, see the [Installation Guide](docs/INSTALLATION.md).

## Quick Start

```bash
# Generate synthetic dataset
blender-synth generate \
    --models ./models \
    --output ./output \
    --num-images 100 \
    --camera-angles 5
```

For more examples and detailed usage, see the [Quick Start Guide](docs/QUICKSTART.md) and [Usage Guide](docs/USAGE.md).

## Repository Structure

```
blender-synth/
├── blender_synth/          # Main package source code
│   ├── core/               # Core functionality (scene, camera, physics)
│   ├── objects/            # Object loading and management
│   ├── pipeline/           # Generation pipeline
│   ├── annotation/         # YOLO annotation generation
│   ├── randomization/      # Domain randomization (lighting, materials)
│   └── utils/              # Utility functions
├── tests/                  # Test suite
│   └── README.md           # Test documentation
├── scripts/                # Utility and debug scripts
│   ├── utils/              # Production utilities (e.g., visualize_annotations.py)
│   ├── debug/              # Development debug scripts
│   └── README.md           # Scripts documentation
├── examples/               # Example usage scripts
├── configs/                # Configuration file templates
├── models/                 # Input 3D models (gitignored)
└── docs/                   # Additional documentation
```

### Input (3D Models)
```
models/
├── pottery/
│   ├── pot_001.obj
│   ├── pot_002.obj
│   └── ...
├── tools/
│   ├── tool_001.obj
│   └── ...
└── ornaments/
    └── ...
```

Directory names become class labels automatically.

### Output (Generated Dataset)
```
output/
├── train/
│   ├── images/
│   │   ├── train_000000.jpg
│   │   └── ...
│   └── labels/
│       ├── train_000000.txt  # YOLO format
│       └── ...
├── val/
│   ├── images/
│   └── labels/
├── test/
│   ├── images/
│   └── labels/
└── classes.txt
```

## Configuration

You can customize generation using YAML configuration files:

```yaml
# config.yaml
models:
  max_per_scene: 5
  scale_range: [0.8, 1.2]

camera:
  nadir_angle_range: [0, 15]  # degrees from vertical
  orbit_angles: 8  # number of camera positions
  distance_range: [0.8, 1.5]  # meters from scene center
  resolution: [1920, 1080]

physics:
  enabled: true
  drop_height: 0.3  # meters
  simulation_steps: 100

lighting:
  num_lights: [2, 4]
  intensity_range: [20, 80]  # Watts - appropriate for indoor artifact photography
  color_temp_range: [3000, 6500]  # Kelvin

background:
  use_drawer_texture: true
  randomize_color: true
  color_variation: 0.2

rendering:
  samples: 128
  max_bounces: 4
  use_denoising: true

dataset:
  train_split: 0.7
  val_split: 0.15
  test_split: 0.15
```

Then use it:

```bash
blender-synth generate --config config.yaml --models ./models --output ./output
```

## Python API

```python
from blender_synth import SyntheticGenerator, GenerationConfig

# Configure generation
config = GenerationConfig(
    model_dir="./models",
    output_dir="./output",
    num_images=100,
    create_visualizations=True,  # Automatically create annotated preview images
)

# Customize settings
config.camera.orbit_angles = 8
config.camera.nadir_angle_range = (0, 15)
config.models.max_per_scene = 5

# Generate dataset
generator = SyntheticGenerator(config)
generator.generate()
```

### Visualization Feature

Set `create_visualizations=True` to automatically generate annotated preview images:
- Visualizations show bounding boxes overlaid on generated images
- Saved to `output/visualizations/` with separate folders for train/val/test
- Useful for quickly verifying annotation quality
- Requires `opencv-python` (installed by default)

## Development

### Running Tests
```bash
# Run main generation test
blenderproc run tests/test_generation.py

# Or use the helper script
./run_blender_synth.sh tests/test_generation.py
```

See `tests/README.md` for more test information.

### Utility Scripts
```bash
# Visualize generated annotations
python scripts/utils/visualize_annotations.py
```

See `scripts/README.md` for more utility information.

## Requirements

- Python 3.9+
- BlenderProc (automatically installs Blender)
- GPU recommended for faster rendering (CUDA/OptiX supported)

## License

MIT

## Acknowledgments

Built with [BlenderProc](https://github.com/DLR-RM/BlenderProc) for simplified Blender integration.
