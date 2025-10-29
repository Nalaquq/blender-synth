import blenderproc as bproc

"""Test script for blender-synth with small dataset.

For GPU support, run this script using the shell launcher which sets up CUDA paths:
    ./run_blender_synth.sh

Or manually set LD_LIBRARY_PATH:
    export LD_LIBRARY_PATH=/usr/lib/wsl/lib:/usr/local/cuda/lib64:$LD_LIBRARY_PATH
    blenderproc run test_generation.py
"""

import sys
from pathlib import Path

# Add parent directory (repository root) to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from blender_synth import SyntheticGenerator, GenerationConfig

def main():
    """Generate a small test synthetic dataset."""

    # Create configuration for minimal test
    config = GenerationConfig(
        model_dir=Path("./models"),  # Use existing models directory
        output_dir=Path("./test_output"),
        num_images=10,  # 10 images for testing
        random_seed=42,
        create_visualizations=True,  # Test visualization feature
    )

    # Customize settings for faster generation
    config.camera.orbit_angles = 1  # Just 1 angle instead of 8
    config.camera.nadir_angle_range = (0, 10)  # Small range
    config.models.max_per_scene = 1  # One object per scene
    config.physics.enabled = True
    config.rendering.samples = 128  # Low samples for faster rendering

    # Create generator
    generator = SyntheticGenerator(config)

    # Generate dataset
    print("Generating small test synthetic dataset...")
    print(f"Model directory: {config.model_dir}")
    print(f"Output directory: {config.output_dir}")
    print(f"Number of images: {config.num_images}")

    generator.generate()

    print(f"\nDone! Dataset saved to {config.output_dir}")


if __name__ == "__main__":
    main()
