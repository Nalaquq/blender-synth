import blenderproc as bproc

"""Sample dataset generation with GPU support test.

This script generates a full sample dataset to test GPU rendering.
Includes train/val/test splits with multiple images.
"""

import sys
from pathlib import Path

# Add blender_synth to path
sys.path.insert(0, str(Path(__file__).parent))

from blender_synth import SyntheticGenerator, GenerationConfig


def main():
    """Generate a sample synthetic dataset with GPU."""

    print("=" * 70)
    print("GPU SAMPLE DATASET GENERATION TEST")
    print("=" * 70)

    # Create configuration for sample dataset
    config = GenerationConfig(
        model_dir=Path("./models"),
        output_dir=Path("./gpu_sample_output"),
        num_images=20,  # 20 images total: 14 train, 3 val, 3 test
        random_seed=42,
    )

    # Optimize settings for faster generation while showing GPU capabilities
    config.camera.orbit_angles = 2  # 2 angles per scene
    config.camera.nadir_angle_range = (0, 20)  # Slight angle variation
    config.models.max_per_scene = 2  # 1-2 objects per scene
    config.models.min_per_scene = 1
    config.physics.enabled = True
    config.rendering.samples = 256  # Good quality for GPU test
    config.rendering.use_gpu = True  # Enable GPU

    # Create generator
    generator = SyntheticGenerator(config)

    # Generate dataset
    print(f"\nConfiguration:")
    print(f"  Model directory: {config.model_dir}")
    print(f"  Output directory: {config.output_dir}")
    print(f"  Total images: {config.num_images}")
    print(f"  Render samples: {config.rendering.samples}")
    print(f"  Objects per scene: {config.models.min_per_scene}-{config.models.max_per_scene}")
    print(f"  GPU enabled: {config.rendering.use_gpu}")
    print()

    generator.generate()

    print("\n" + "=" * 70)
    print(f"DATASET GENERATION COMPLETE!")
    print(f"Dataset saved to: {config.output_dir}")
    print("=" * 70)


if __name__ == "__main__":
    main()
