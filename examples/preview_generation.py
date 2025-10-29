"""Example of generating preview images for quick testing."""

from pathlib import Path
from blender_synth import SyntheticGenerator, GenerationConfig

def main():
    """Generate a small preview dataset for testing."""

    # Create configuration with fast settings
    config = GenerationConfig(
        model_dir=Path("./models"),
        output_dir=Path("./preview"),
        num_images=10,  # Small number for testing
        random_seed=42,
    )

    # Use fast settings
    config.camera.orbit_angles = 4  # Fewer angles
    config.camera.resolution = (1280, 720)  # Lower resolution
    config.rendering.engine = "EEVEE"  # Faster rendering
    config.rendering.samples = 32  # Fewer samples
    config.models.max_per_scene = 3
    config.physics.simulation_steps = 50

    # Create generator
    generator = SyntheticGenerator(config)

    # Generate preview
    print("Generating preview images...")
    generator.generate_preview(num_images=10)

    print(f"Preview saved to {config.output_dir}/preview")


if __name__ == "__main__":
    main()
