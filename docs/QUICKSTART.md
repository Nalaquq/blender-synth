# Quick Start Guide

Get started generating synthetic datasets in 5 minutes!

## 1. Install

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install
pip install -e .
```

**That's it!** No manual Blender installation needed. BlenderProc handles it automatically.

## 2. Organize Your 3D Models

Create a directory structure:

```
models/
├── class1/
│   ├── model1.obj
│   └── model2.glb
├── class2/
│   └── model3.obj
└── class3/
    └── model4.obj
```

For archaeological artifacts:
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

## 3. Generate Your First Dataset

**Option A: Command Line**

```bash
blender-synth generate \
    --models ./models \
    --output ./output \
    --num-images 100
```

**Option B: Python Script**

```python
from pathlib import Path
from blender_synth import SyntheticGenerator, GenerationConfig

config = GenerationConfig(
    model_dir=Path("./models"),
    output_dir=Path("./output"),
    num_images=100,
)

generator = SyntheticGenerator(config)
generator.generate()
```

**Option C: Configuration File**

```bash
blender-synth generate --config configs/default.yaml
```

## 4. First Run Note

On the **first run**, BlenderProc will download Blender automatically (this takes a few minutes, but only happens once):

```
Downloading Blender...
Extracting Blender...
Initializing BlenderProc...
Starting generation...
```

## 5. Check Your Results

Your dataset will be in the output directory:

```
output/
├── train/
│   ├── images/      # Training images
│   └── labels/      # YOLO annotations
├── val/
│   ├── images/
│   └── labels/
├── test/
│   ├── images/
│   └── labels/
└── classes.txt      # Class names
```

## What Just Happened?

The generator:
1. ✓ Loaded your 3D models
2. ✓ Dropped them onto a table using physics
3. ✓ Positioned cameras overhead (nadir/near-nadir angles)
4. ✓ Randomized lighting, materials, and backgrounds
5. ✓ Rendered photorealistic images
6. ✓ Generated YOLO format annotations
7. ✓ Split into train/val/test sets

## Customize for Museum Drawers

For archaeological artifact photography from above:

```python
config = GenerationConfig(
    model_dir=Path("./models"),
    output_dir=Path("./output"),
    num_images=500,
)

# Nadir photography (overhead view)
config.camera.nadir_angle_range = (0, 15)  # 0-15° from vertical
config.camera.orbit_angles = 12  # 12 viewpoints around scene
config.camera.distance_range = (0.8, 1.5)  # meters

# Indoor museum/archival lighting
config.lighting.intensity_range = (30, 80)  # Appropriate for close-up photography
config.lighting.color_temp_range = (4000, 5500)  # Neutral white

# Drawer-like surface
config.background.use_drawer_texture = True
config.background.base_color = (0.8, 0.75, 0.7)  # Light wood

generator = SyntheticGenerator(config)
generator.generate()
```

## Speed Tips

### Fast Preview (for testing)

```bash
blender-synth generate \
    --config configs/fast_preview.yaml \
    --models ./models \
    --output ./preview
```

### High Quality (for production)

```bash
blender-synth generate \
    --config configs/high_quality.yaml \
    --models ./models \
    --output ./dataset_final
```

## Next Steps

- **Read**: [USAGE.md](USAGE.md) for detailed configuration options
- **Explore**: [examples/](examples/) for Python scripts
- **Customize**: [configs/](configs/) for different quality presets

## Common Issues

**"No models found"**
- Check your models directory structure
- Ensure models are in subdirectories (class names)
- Supported formats: .obj, .glb, .gltf, .ply, .stl, .fbx

**Slow rendering**
- Enable GPU: `config.rendering.use_gpu = True`
- Lower samples: `config.rendering.samples = 32`
- Use EEVEE: `config.rendering.engine = "EEVEE"`

**No annotations**
- Objects may be falling through table - increase physics steps
- Camera may not see objects - check distance range

## Full Documentation

- [README.md](README.md) - Overview and features
- [INSTALLATION.md](INSTALLATION.md) - Detailed installation
- [USAGE.md](USAGE.md) - Complete usage guide
- [examples/](examples/) - Example scripts

Happy generating! 🎨
