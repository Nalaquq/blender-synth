# Memory Monitoring

The dataset generator includes comprehensive memory monitoring to help you track resource usage during long generation runs.

## What Gets Logged

### 1. Console and Log File Output

During generation, you'll see periodic memory updates in both the terminal and log files:

```
2025-10-31 12:00:00 - blender_synth - INFO - Memory: 2.45 GB (2508 MB) | Images: 50 | Peak: 2.67 GB | Blender data blocks - Meshes: 23, Materials: 45, Textures: 12, Images: 8
```

**Logging Frequency:**
- Every 10 images for the first 100 images (to catch early memory leaks)
- Every 50 images thereafter

### 2. Memory Usage CSV (`memory_usage.csv`)

A detailed CSV file is saved to your log directory with memory measurements at each logging interval:

**Location:** `<output_dir>/logs/<run_type>_<timestamp>/memory_usage.csv`

**Columns:**
- `timestamp` - Unix timestamp of measurement
- `images_generated` - Number of images generated so far
- `memory_mb` - Current memory usage in MB
- `memory_gb` - Current memory usage in GB
- `meshes` - Number of Blender mesh data blocks
- `materials` - Number of Blender material data blocks
- `textures` - Number of Blender texture data blocks
- `images` - Number of Blender image data blocks

**Example:**
```csv
timestamp,images_generated,memory_mb,memory_gb,meshes,materials,textures,images
1698765432.123,10,2340.5,2.29,23,45,12,8
1698765445.678,20,2356.2,2.30,24,46,12,8
1698765458.901,30,2348.9,2.29,23,45,12,8
```

### 3. Generation Summary (`generation_summary.json`)

The summary JSON now includes peak memory usage:

```json
{
  "total_images": 10000,
  "train_images": 7000,
  "val_images": 1500,
  "test_images": 1500,
  "elapsed_time_seconds": 3600.5,
  "peak_memory_mb": 2890.3,
  "peak_memory_gb": 2.82,
  "device_type": "GPU"
}
```

## How to Use This Information

### Identifying Memory Leaks

A healthy memory profile should look like this:
```
Images:    0 -> Memory: 1.8 GB
Images:   10 -> Memory: 2.3 GB  (initial ramp-up)
Images:   50 -> Memory: 2.4 GB  (stabilized)
Images:  100 -> Memory: 2.4 GB  (stable)
Images:  500 -> Memory: 2.5 GB  (stable)
Images: 5000 -> Memory: 2.6 GB  (stable)
```

A memory leak would look like this:
```
Images:    0 -> Memory: 1.8 GB
Images:   10 -> Memory: 2.3 GB
Images:   50 -> Memory: 4.2 GB  ⚠️ growing
Images:  100 -> Memory: 7.8 GB  ⚠️ growing rapidly
Images:  150 -> CRASHED (OOM)   ❌
```

### Analyzing with Spreadsheet

1. Open `memory_usage.csv` in Excel, Google Sheets, or any spreadsheet software
2. Create a line chart with:
   - X-axis: `images_generated`
   - Y-axis: `memory_gb`
3. Add additional lines for `meshes`, `materials`, etc. to identify which resources are accumulating

### Monitoring Blender Data Blocks

The data block counts help identify what's accumulating in memory:
- **Meshes** - Should stay low (< 50) after stabilization
- **Materials** - Should stay low (< 100) after stabilization
- **Textures** - Should stay low (< 50) after stabilization
- **Images** - Should stay low (< 50) after stabilization

If these numbers keep growing, it indicates the cleanup process isn't working properly.

## System Requirements

To avoid OOM crashes:
- **Minimum RAM:** 8 GB (for small batches < 1000 images)
- **Recommended RAM:** 16 GB (for 10,000+ image generations)
- **GPU RAM:** 6+ GB VRAM for GPU rendering

## Troubleshooting

### Still Getting OOM Crashes?

1. **Check peak memory** in `generation_summary.json`
2. **Review memory trend** in `memory_usage.csv`
3. **Reduce concurrent objects:**
   ```yaml
   models:
     max_per_scene: 15  # Reduce from 30
   ```
4. **Lower rendering samples:**
   ```yaml
   rendering:
     samples: 64  # Reduce from 128
   ```
5. **Process in batches:**
   - Generate 1000 images at a time
   - Restart between batches to clear all memory

### Memory Growing Despite Cleanup?

Check the Blender data block counts in the logs. If they're increasing:
- Open an issue at https://github.com/your-repo/issues
- Include the `memory_usage.csv` file
- Include the last 100 lines of the log file
