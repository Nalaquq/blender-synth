"""Basic example of synthetic data generation."""

from pathlib import Path
from blender_synth import SyntheticGenerator, GenerationConfig

def main():
    """Generate a basic synthetic dataset."""

    # Create configuration
    config = GenerationConfig(
        model_dir=Path("./models"),  # Directory with your 3D models
        output_dir=Path("./output"),
        num_images=100,
        random_seed=42,
    )

    # Optional: Customize settings
    config.camera.orbit_angles = 8
    config.camera.nadir_angle_range = (0, 15)  # 0-15 degrees from vertical
    config.models.max_per_scene = 5
    config.physics.enabled = True

    # Create generator
    generator = SyntheticGenerator(config)

    # Generate dataset
    print("Generating synthetic dataset...")
    generator.generate()

    print(f"Done! Dataset saved to {config.output_dir}")


if __name__ == "__main__":
    main()
