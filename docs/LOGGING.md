# Logging System

The blender-synth package now includes comprehensive logging functionality that automatically creates log directories and files for each dataset generation or test run.

## Features

- **Automatic Log Directory Creation**: Each run creates a timestamped log directory
- **Comprehensive Logging**: Both console and file output
- **Run Metadata**: JSON files with configuration and parameters
- **Performance Statistics**: Execution time and performance metrics
- **Debug Information**: Detailed logs for troubleshooting

## Log Directory Structure

When you run a generation or preview command, logs are automatically created in the output directory:

```
output_dir/
├── logs/
│   ├── generation_YYYYMMDD_HHMMSS/
│   │   ├── generation.log            # Detailed execution log
│   │   ├── run_metadata.json         # Run configuration and parameters
│   │   └── generation_summary.json   # Performance statistics
│   └── preview_YYYYMMDD_HHMMSS/
│       ├── preview.log
│       ├── run_metadata.json
│       └── preview_summary.json
├── train/
├── val/
└── test/
```

## Log Files

### 1. Execution Log (`generation.log` or `preview.log`)

Contains detailed execution information:
- Initialization steps
- Model discovery
- Rendering progress
- Warnings and errors
- Completion statistics

Example:
```
2025-10-29 09:57:03 - blender_synth - INFO - Starting synthetic data generation
2025-10-29 09:57:03 - blender_synth - INFO - Configuration: 100 images total
2025-10-29 09:57:03 - blender_synth - INFO - Initializing BlenderProc
2025-10-29 09:57:03 - blender_synth - INFO - RENDERING MODE: GPU
```

### 2. Run Metadata (`run_metadata.json`)

Contains the configuration and parameters used for the run:
```json
{
  "command": "generation",
  "timestamp": "2025-10-29T09:57:03.934636",
  "arguments": {
    "models": "./models",
    "output": "./output",
    "num_images": 100,
    "camera_angles": 8,
    "max_objects": 5,
    "resolution": [1920, 1080],
    "seed": 42,
    "physics_enabled": true,
    "engine": "CYCLES",
    "samples": 128
  },
  "config_file": "./configs/default.yaml"
}
```

### 3. Generation Summary (`generation_summary.json` or `preview_summary.json`)

Contains performance statistics and dataset information:
```json
{
  "total_images": 100,
  "train_images": 70,
  "val_images": 15,
  "test_images": 15,
  "num_classes": 5,
  "class_names": ["arrowhead", "pottery", "bone", "tool", "ornament"],
  "elapsed_time_seconds": 3456.78,
  "elapsed_time_minutes": 57.61,
  "avg_time_per_image": 34.57,
  "device_type": "GPU",
  "output_directory": "./output"
}
```

## Usage

### Command-Line Interface

Logging is automatically enabled when using the CLI:

```bash
# Generate dataset - logs will be created automatically
blender-synth generate --models ./models --output ./output --num-images 100

# Preview generation - logs will be created automatically
blender-synth preview --models ./models --output ./preview --num-images 5
```

### Python API

When using the Python API, you can optionally provide a logger and log directory:

```python
from pathlib import Path
from blender_synth.pipeline.config import GenerationConfig
from blender_synth.pipeline.generator import SyntheticGenerator
from blender_synth.utils.logger import create_log_directory, setup_run_logger

# Create configuration
config = GenerationConfig(
    model_dir=Path("./models"),
    output_dir=Path("./output"),
    num_images=100,
)

# Create log directory
log_dir = create_log_directory(config.output_dir, run_type="generation")

# Set up logger
logger = setup_run_logger(log_dir, run_type="generation")

# Create generator with logger
generator = SyntheticGenerator(config, logger=logger, log_dir=log_dir)
generator.generate()
```

## Viewing Logs

### During Execution

Logs are displayed in real-time on the console during generation.

### After Execution

1. Navigate to the output directory:
   ```bash
   cd output/logs
   ```

2. Find the most recent run:
   ```bash
   ls -lt
   ```

3. View the log file:
   ```bash
   cat generation_YYYYMMDD_HHMMSS/generation.log
   ```

4. View the metadata:
   ```bash
   cat generation_YYYYMMDD_HHMMSS/run_metadata.json | python -m json.tool
   ```

5. View the summary:
   ```bash
   cat generation_YYYYMMDD_HHMMSS/generation_summary.json | python -m json.tool
   ```

## Debugging

When debugging issues:

1. Check the execution log for errors and warnings
2. Verify the configuration in `run_metadata.json`
3. Review performance metrics in the summary file
4. Compare logs from successful vs. failed runs

## Testing

To test the logging functionality:

```bash
python test_logging.py
```

This will create test log directories in `./test_output/logs/` and `./test_logs/` for verification.

## Log Retention

Log files are kept indefinitely. You may want to periodically clean up old logs:

```bash
# Remove logs older than 30 days
find output/logs -type d -name "*_*" -mtime +30 -exec rm -rf {} \;
```

## Benefits

- **Reproducibility**: Run metadata allows you to reproduce results
- **Debugging**: Detailed logs help identify and fix issues
- **Performance Monitoring**: Track generation speed and efficiency
- **Audit Trail**: Keep records of all dataset generations
- **Troubleshooting**: Compare successful and failed runs
