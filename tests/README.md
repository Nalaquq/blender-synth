# Tests

This directory contains test scripts for the blender-synth package.

## Test Scripts

### Unit/Integration Tests
- `test_generation.py` - Main test for complete dataset generation pipeline
- `test_memory_fix.py` - Memory leak fix verification (100 images with monitoring)
- `test_annotation_fix.py` - Tests annotation generation with fixes
- `test_gpu_sample.py` - Tests GPU rendering with sample generation

### GPU Tests
- `test_gpu_detection.py` - Tests GPU detection functionality
- `test_blender_gpu_info.py` - Tests Blender GPU information retrieval

### Segmentation Tests
- `test_physics_segmentation.py` - Tests physics simulation with segmentation
- `test_with_physics_only.py` - Tests physics-only segmentation
- `test_object_visibility.py` - Tests object visibility in rendered scenes
- `test_class_instance.py` - Tests class and instance mapping
- `test_map_by_fix.py` - Tests segmentation map_by parameter fix
- `test_enable_after_load.py` - Tests enable segmentation after object loading
- `test_multiple_renders.py` - Tests multiple render cycles

## Running Tests

### Prerequisites
Make sure you have set up the environment:
```bash
# From repository root
source venv/bin/activate
export LD_LIBRARY_PATH=/usr/lib/wsl/lib:/usr/local/cuda/lib64:$LD_LIBRARY_PATH
```

### Run a specific test
```bash
# From repository root
./run_blender_synth.sh tests/test_generation.py

# Or directly with blenderproc
blenderproc run tests/test_generation.py
```

### Quick Test
For a quick functionality test:
```bash
blenderproc run tests/test_generation.py
```

### Memory Leak Test
To verify the memory leak fix with 100 images:
```bash
./run_blender_synth.sh tests/test_memory_fix.py
```

This test will:
- Generate 100 images
- Monitor memory usage every 10 images
- Export memory metrics to CSV
- Verify memory stays stable (no unbounded growth)

## Test Output
Tests generate output in temporary directories that are automatically cleaned up.
Default output locations:
- `test_output/` - Main test output (gitignored)
- `output/memory_test/` - Memory fix test output (gitignored)
- `annotation_test_output/` - Annotation test output (gitignored)
- `gpu_sample_output/` - GPU sample output (gitignored)

## Notes
- All tests require BlenderProc to be installed
- GPU tests require CUDA/GPU support
- Tests are designed to be run from the repository root
