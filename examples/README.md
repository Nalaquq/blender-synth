# Examples Directory

This directory contains example Python scripts demonstrating various use cases for blender-synth.

## Available Examples

### 1. `basic_generation.py`
The simplest example - generates a dataset with default settings.

**Usage**:
```bash
python examples/basic_generation.py
```

**What it does**:
- Loads models from `./models`
- Generates 100 images
- Uses default camera and physics settings
- Saves to `./output`

**Good for**: First-time users, understanding the basic API

---

### 2. `config_based_generation.py`
Demonstrates loading configuration from YAML files.

**Usage**:
```bash
python examples/config_based_generation.py
```

**What it does**:
- Loads `configs/default.yaml`
- Overrides specific settings
- Generates 200 images

**Good for**: Production workflows, team collaboration, reproducibility

---

### 3. `preview_generation.py`
Quick preview generation for testing your models.

**Usage**:
```bash
python examples/preview_generation.py
```

**What it does**:
- Fast rendering settings (EEVEE, low samples)
- Lower resolution
- Only 10 images
- Saves to `./preview`

**Good for**: Testing model compatibility, quick iteration

---

### 4. `custom_camera_angles.py`
Advanced example showing custom camera configuration.

**Usage**:
```bash
python examples/custom_camera_angles.py
```

**What it does**:
- Pure nadir camera (0-5° from vertical)
- 12 camera positions
- Square images (2048x2048)
- Custom lighting setup

**Good for**: Specialized photography angles, custom viewpoints

---

## Running Examples

### Before You Start

1. **Install the package**:
   ```bash
   pip install -e .
   ```

2. **Prepare your models**:
   Create a `models/` directory in the project root:
   ```
   models/
   ├── class1/
   │   └── model1.obj
   ├── class2/
   │   └── model2.obj
   └── class3/
       └── model3.glb
   ```

3. **Run an example**:
   ```bash
   python examples/basic_generation.py
   ```

### Modifying Examples

All examples are designed to be easily customized. Simply:

1. Copy an example to your own script
2. Modify the configuration
3. Run it!

Example:
```bash
cp examples/basic_generation.py my_custom_script.py
# Edit my_custom_script.py
python my_custom_script.py
```

## Common Customizations

### Change Number of Images

```python
config.num_images = 500  # Generate 500 images
```

### Change Camera Settings

```python
# More overhead angles
config.camera.nadir_angle_range = (0, 5)  # Nearly vertical
config.camera.orbit_angles = 16  # More viewpoints
```

### Change Rendering Quality

```python
# High quality
config.rendering.engine = "CYCLES"
config.rendering.samples = 256
config.camera.resolution = (2560, 1440)

# Fast preview
config.rendering.engine = "EEVEE"
config.rendering.samples = 32
config.camera.resolution = (1280, 720)
```

### Change Physics

```python
# More objects, more physics steps
config.models.max_per_scene = 8
config.physics.simulation_steps = 150
```

### Disable Physics

```python
# Just random placement, no simulation
config.physics.enabled = False
```

## Troubleshooting

### "No models found"
Make sure your models are in subdirectories:
```
models/
├── class1/  ← Directory names are class labels
│   └── *.obj
└── class2/
    └── *.glb
```

### "BlenderProc downloading..."
This is normal on first run. BlenderProc downloads Blender automatically. Subsequent runs will be faster.

### Rendering too slow
Try the preview example or adjust settings:
```python
config.rendering.samples = 32  # Lower samples
config.rendering.engine = "EEVEE"  # Faster engine
```

### Out of memory
Reduce resolution or number of objects:
```python
config.camera.resolution = (1280, 720)
config.models.max_per_scene = 3
```

## Next Steps

After running the examples:

1. **Review output**: Check `output/` or `preview/` directories
2. **Customize**: Modify examples for your specific use case
3. **Scale up**: Generate larger datasets with high-quality settings
4. **Train models**: Use the generated YOLO annotations to train object detection models

## Additional Resources

- [USAGE.md](../docs/USAGE.md) - Complete configuration reference
- [configs/](../configs/) - Pre-built configuration templates
- [QUICKSTART.md](../docs/QUICKSTART.md) - 5-minute quick start guide
- [Documentation Index](../docs/index.md) - Full documentation
