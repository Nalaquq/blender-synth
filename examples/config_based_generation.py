"""Example of generating dataset from YAML configuration."""

from pathlib import Path
from blender_synth import SyntheticGenerator, GenerationConfig

def main():
    """Generate dataset using YAML configuration file."""

    # Load configuration from YAML
    config = GenerationConfig.from_yaml(Path("configs/default.yaml"))

    # Override specific settings if needed
    config.model_dir = Path("./models")  # Update paths as needed
    config.output_dir = Path("./output")
    config.num_images = 200  # Override number of images

    # Create generator and run
    generator = SyntheticGenerator(config)
    generator.generate()

    print(f"Dataset generated and saved to {config.output_dir}")


if __name__ == "__main__":
    main()
