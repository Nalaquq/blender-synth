# Usage Guide

## Command Line Interface

### Basic Usage

Generate a dataset with default settings:

```bash
blender-synth generate --models ./models --output ./output --num-images 100
```

### Full Options

```bash
blender-synth generate \
    --models ./models \
    --output ./output \
    --num-images 1000 \
    --camera-angles 12 \
    --max-objects 5 \
    --resolution 1920 1080 \
    --seed 42 \
    --engine CYCLES \
    --samples 128
```

### Using Configuration Files

Create a custom config (or use one from `configs/`):

```bash
blender-synth generate --config configs/high_quality.yaml
```

Override config values:

```bash
blender-synth generate \
    --config configs/default.yaml \
    --num-images 500 \
    --output ./my_output
```

### Preview Mode

Generate a small preview dataset for testing:

```bash
blender-synth preview --models ./models --output ./preview --num-images 5
```

## Python API

### Basic Example

```python
from pathlib import Path
from blender_synth import SyntheticGenerator, GenerationConfig

# Create configuration
config = GenerationConfig(
    model_dir=Path("./models"),
    output_dir=Path("./output"),
    num_images=100,
    random_seed=42,
)

# Generate dataset
generator = SyntheticGenerator(config)
generator.generate()
```

### Custom Configuration

```python
from blender_synth import GenerationConfig

config = GenerationConfig(
    model_dir=Path("./models"),
    output_dir=Path("./output"),
    num_images=500,
)

# Customize camera (nadir photography)
config.camera.nadir_angle_range = (0, 10)  # Nearly vertical
config.camera.orbit_angles = 12  # 12 viewpoints
config.camera.distance_range = (0.8, 1.5)
config.camera.resolution = (2048, 2048)  # Square images

# Customize physics
config.physics.enabled = True
config.physics.drop_height = 0.3
config.physics.simulation_steps = 100

# Customize rendering
config.rendering.engine = "CYCLES"
config.rendering.samples = 256  # High quality
config.rendering.use_gpu = True

# Customize lighting
config.lighting.num_lights = (3, 5)
config.lighting.intensity_range = (20, 80)  # Lower values for indoor scenes
config.lighting.color_temp_range = (3000, 6500)

# Generate
generator = SyntheticGenerator(config)
generator.generate()
```

### Load from YAML

```python
config = GenerationConfig.from_yaml(Path("configs/default.yaml"))

# Override specific settings
config.model_dir = Path("./my_models")
config.num_images = 1000

generator = SyntheticGenerator(config)
generator.generate()
```

## Configuration Options

### Camera Settings

Control camera positioning for nadir/near-nadir photography:

```yaml
camera:
  # Angle from vertical (0 = pure nadir, 90 = horizontal)
  nadir_angle_range: [0, 15]  # 0-15 degrees from vertical

  # Number of camera positions around the scene
  orbit_angles: 8

  # Distance from scene center
  distance_range: [0.8, 1.5]  # meters

  # Output resolution
  resolution: [1920, 1080]

  # Focal length
  focal_length: 50.0  # mm
```

### Physics Settings

Control how objects are dropped onto the table:

```yaml
physics:
  enabled: true
  drop_height: 0.3  # meters above table
  simulation_steps: 100  # more = more accurate but slower
  gravity: [0, 0, -9.81]
  friction: 0.5  # 0-1
  restitution: 0.3  # bounciness, 0-1
```

### Lighting Settings

Randomize lighting for domain randomization:

```yaml
lighting:
  num_lights: [2, 4]  # random between 2-4 lights
  intensity_range: [20, 80]  # Watts - appropriate for indoor close-up photography
  color_temp_range: [3000, 6500]  # Kelvin (warm to cool)
  use_hdri: false  # HDRI environment maps
```

### Background Settings

Configure the drawer/table surface:

```yaml
background:
  use_drawer_texture: true
  randomize_color: true
  color_variation: 0.2  # amount of variation
  base_color: [0.8, 0.75, 0.7]  # RGB, light wood color
```

### Rendering Settings

```yaml
rendering:
  engine: CYCLES  # or EEVEE
  samples: 128  # higher = better quality, slower
  max_bounces: 4  # light bounces
  use_denoising: true
  use_gpu: true
```

### Model Settings

```yaml
models:
  max_per_scene: 5  # max objects per image
  min_per_scene: 1  # min objects per image
  scale_range: [0.8, 1.2]  # random scaling
  randomize_rotation: true
```

### Dataset Split

```yaml
dataset:
  train_split: 0.7  # 70% training
  val_split: 0.15   # 15% validation
  test_split: 0.15  # 15% test
```

## Output Format

### Directory Structure

```
output/
├── train/
│   ├── images/
│   │   ├── train_000000.jpg
│   │   ├── train_000001.jpg
│   │   └── ...
│   └── labels/
│       ├── train_000000.txt
│       ├── train_000001.txt
│       └── ...
├── val/
│   ├── images/
│   └── labels/
├── test/
│   ├── images/
│   └── labels/
├── classes.txt
└── config.yaml
```

### YOLO Annotation Format

Each `.txt` file contains one line per object:

```
<class_id> <x_center> <y_center> <width> <height>
```

All values are normalized to [0, 1]:
- `class_id`: Integer class index (from `classes.txt`)
- `x_center`: Center X coordinate (0-1)
- `y_center`: Center Y coordinate (0-1)
- `width`: Bounding box width (0-1)
- `height`: Bounding box height (0-1)

Example:
```
0 0.512 0.458 0.234 0.156
2 0.789 0.623 0.145 0.098
```

### Classes File

`classes.txt` contains one class name per line:

```
pottery
tools
ornaments
```

The line number (0-indexed) is the class ID used in annotations.

## Tips and Best Practices

### For Museum Drawer Photography

1. **Use narrow nadir angle range** for realistic overhead shots:
   ```yaml
   camera:
     nadir_angle_range: [0, 10]
   ```

2. **Multiple orbit positions** for diverse viewpoints:
   ```yaml
   camera:
     orbit_angles: 12
   ```

3. **Indoor lighting** to simulate museum/archival conditions:
   ```yaml
   lighting:
     intensity_range: [30, 80]  # Appropriate for indoor artifact photography
     color_temp_range: [4000, 5500]  # Neutral indoor lighting
   ```

### For Training Robust Models

1. **Use strong domain randomization**:
   - Wide lighting variation
   - Variable object counts
   - Different scales and rotations

2. **Generate large datasets**:
   - Minimum 500-1000 images per class
   - More is better for deep learning

3. **Balance your classes**:
   - Ensure similar numbers of models per class
   - Or generate multiple passes

### Performance Optimization

1. **Fast iteration** (use `fast_preview.yaml`):
   - EEVEE renderer
   - Low samples (32)
   - Lower resolution
   - Fewer simulation steps

2. **Production quality** (use `high_quality.yaml`):
   - CYCLES renderer
   - High samples (256+)
   - High resolution
   - More camera angles

3. **GPU acceleration**:
   - Always enable if available
   - Can be 5-10x faster than CPU

## Troubleshooting

### No annotations generated

- Check that models are loading correctly
- Ensure physics simulation completes
- Verify objects are visible in camera view

### Poor quality renders

- Increase `rendering.samples`
- Enable `rendering.use_denoising`
- Use CYCLES instead of EEVEE

### Slow generation

- Use `configs/fast_preview.yaml`
- Reduce `rendering.samples`
- Lower `camera.resolution`
- Enable GPU rendering
- Reduce `physics.simulation_steps`

### Objects falling through table

- Increase `physics.simulation_steps`
- Check object scales
- Verify collision shapes

## Examples

See the [examples/](examples/) directory for complete Python scripts demonstrating various use cases.
