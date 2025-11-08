# Memory Leak Fix - November 2025

## Problem Summary

The dataset generator was experiencing Out-of-Memory (OOM) crashes after generating ~110 images during large dataset generation runs (1000+ images). The process was being killed by the Linux OOM killer.

### Evidence
- System logs showed OOM kill at `2025-11-06 00:51:02`
- Process was using ~52GB virtual memory and ~9.3GB resident memory when killed
- Generation stopped at image 110 out of 1000 requested
- No error message in application logs - silent termination

### Root Cause

While basic cleanup was in place (deleting objects, clearing data blocks), the memory leak was caused by:

1. **Incomplete render data cleanup**: The render data dictionary contains multiple large numpy arrays (colors, normals, depth, segmentation maps) that weren't being explicitly cleared before deletion
2. **Blender's undo history accumulation**: Blender accumulates undo/redo history which grows unbounded during long generation runs
3. **Insufficient garbage collection**: Single gc.collect() pass wasn't enough to handle circular references and nested data structures
4. **GPU memory caches**: When using GPU rendering, GPU-side caches weren't being cleared

## Solution Implemented

### 1. Explicit Render Data Component Deletion

Before deleting the render data dictionary, now explicitly delete each component:
```python
if 'colors' in data:
    del data['colors']
if 'normals' in data:
    del data['normals']
if 'depth' in data:
    del data['depth']
if 'instance_segmaps' in data:
    del data['instance_segmaps']
if 'instance_attribute_maps' in data:
    del data['instance_attribute_maps']
del data
```

This ensures no references remain to the large numpy arrays.

### 2. Aggressive Memory Cleanup

Added `_aggressive_memory_cleanup()` method that runs every 10 images:

```python
def _aggressive_memory_cleanup(self):
    # Clear active object reference (background-safe)
    try:
        if bpy.context.view_layer.objects.active:
            bpy.context.view_layer.objects.active = None
    except:
        pass

    # Blender 2.9+ orphans_purge safely removes unused data blocks
    try:
        if hasattr(bpy.data, 'orphans_purge'):
            bpy.data.orphans_purge()
    except:
        pass

    # Multiple garbage collection passes
    gc.collect()  # First pass: circular references
    gc.collect()  # Second pass: objects freed in first pass
    gc.collect()  # Third pass: final cleanup
```

**Note:** This method is safe for background rendering (no UI operations that would cause crashes).

### 3. Multi-Pass Garbage Collection

Changed from single `gc.collect()` to three passes:
- First pass: collects objects with circular references
- Second pass: collects objects that became eligible after first pass
- Third pass: ensures everything is cleaned

## Testing

To verify the fix works:

```bash
# Run a longer generation to test memory stability
blender-synth generate \
  --config configs/high_quality.yaml \
  --num-images 500

# Monitor memory during generation
watch -n 5 'ps aux | grep blender | grep -v grep'

# Check the memory usage CSV after completion
cat output_hq/logs/generation_*/memory_usage.csv
```

Expected behavior after fix:
- Memory should stabilize after initial ramp-up (~50-100 images)
- Peak memory should remain under 4-5GB for typical configurations
- Process should complete all requested images without OOM kills

## Files Modified

- `blender_synth/pipeline/generator.py:74-106` - Added `_aggressive_memory_cleanup()` method
- `blender_synth/pipeline/generator.py:354-371` - Enhanced render data cleanup (failure path)
- `blender_synth/pipeline/generator.py:379-394` - Enhanced render data cleanup (success path)
- `blender_synth/pipeline/generator.py:396-402` - Added periodic aggressive cleanup call

## Configuration Recommendations

If you still experience memory issues:

1. **Reduce objects per scene:**
   ```yaml
   models:
     max_per_scene: 8  # Reduce from default 15
   ```

2. **Lower render samples:**
   ```yaml
   rendering:
     samples: 64  # Reduce from default 128
   ```

3. **Reduce resolution:**
   ```yaml
   camera:
     resolution: [1280, 720]  # Reduce from [2560, 1440]
   ```

4. **Process in batches:**
   ```bash
   # Generate 500 images at a time, restart between batches
   for i in {1..4}; do
     blender-synth generate --num-images 500 --output output_batch_$i
   done
   ```

## Related Issues

- Previous fix (commit 9512fd3): Added basic data block cleanup and memory monitoring
- This fix extends that work with more aggressive cleanup strategies
