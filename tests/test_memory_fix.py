import blenderproc as bproc

"""Test script to verify memory leak fix.

This script generates a small dataset (100 images) and monitors memory usage
to ensure it remains stable and doesn't grow unbounded.

For GPU support, run this script using the shell launcher which sets up CUDA paths:
    ./run_blender_synth.sh tests/test_memory_fix.py

Or manually set LD_LIBRARY_PATH:
    export LD_LIBRARY_PATH=/usr/lib/wsl/lib:/usr/local/cuda/lib64:$LD_LIBRARY_PATH
    blenderproc run tests/test_memory_fix.py
"""

import sys
from pathlib import Path

# Add parent directory (repository root) to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from blender_synth.pipeline.config import GenerationConfig
from blender_synth.pipeline.generator import SyntheticGenerator
from blender_synth.utils.logger import setup_logger

def main():
    """Run memory leak test."""
    # Set up configuration for a small test run
    config = GenerationConfig.from_yaml("configs/default.yaml")

    # Override for smaller test
    config.num_images = 100
    config.output_dir = "./output/memory_test"

    # Set up logger
    logger = setup_logger()
    logger.info("="*60)
    logger.info("MEMORY LEAK FIX TEST")
    logger.info("="*60)
    logger.info("Generating 100 images to verify memory stays stable...")
    logger.info("")

    # Create generator and run
    generator = SyntheticGenerator(config, logger)
    generator.generate()

    logger.info("")
    logger.info("="*60)
    logger.info("TEST COMPLETE")
    logger.info("="*60)
    logger.info("Check the logs above:")
    logger.info("- Memory should stabilize after initial ramp-up")
    logger.info("- Blender data block counts should remain low")
    logger.info("- No OOM crashes should occur")
    logger.info("")
    logger.info("Review detailed metrics:")
    logger.info(f"- Log file: {config.output_dir}/logs/generation_*/generation.log")
    logger.info(f"- Memory CSV: {config.output_dir}/logs/generation_*/memory_usage.csv")
    logger.info(f"- Summary: {config.output_dir}/logs/generation_*/generation_summary.json")

if __name__ == "__main__":
    main()
