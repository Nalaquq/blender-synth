# Scripts

This directory contains utility and debug scripts for blender-synth development.

## Structure

### `utils/` - Utility Scripts
Production-ready utility scripts:
- `check_annotations.py` - Check and validate annotation quality (missing files, empty labels, etc.)
- `visualize_annotations.py` - Visualize YOLO annotations on generated images

### `debug/` - Debug Scripts  
Development and debugging scripts (not for production use):
- `debug_camera_view.py` - Debug camera positioning and view
- `debug_exact_flow.py` - Debug exact generation flow
- `debug_gltf_physics_seg.py` - Debug GLTF loading with physics and segmentation
- `debug_render_keys.py` - Debug render data keys and structure
- `debug_segmentation.py` - Debug segmentation output

## Usage

### Checking Annotations
```bash
# From repository root
source venv/bin/activate
python scripts/utils/check_annotations.py
```

This will:
1. Check for missing annotation files
2. Check for empty annotation files
3. Identify orphaned label files
4. Generate visualizations with bounding boxes
5. Provide statistics on annotation quality

### Visualizing Annotations
```bash
# From repository root
source venv/bin/activate
python scripts/utils/visualize_annotations.py
```

This will:
1. Read images from `test_output/train/images/`
2. Read annotations from `test_output/train/labels/`
3. Generate visualizations in `test_output/visualizations/`

### Running Debug Scripts
```bash
# From repository root
./run_blender_synth.sh scripts/debug/debug_segmentation.py

# Or directly:
blenderproc run scripts/debug/debug_segmentation.py
```

## Notes
- Utility scripts can be run with regular Python
- Debug scripts require BlenderProc and should be run via `run_blender_synth.sh` or `blenderproc run`
- Debug scripts are for development only and may require manual configuration
