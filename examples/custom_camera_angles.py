"""Example showing custom camera angle configuration."""

from pathlib import Path
import numpy as np
from blender_synth import SyntheticGenerator, GenerationConfig

def main():
    """Generate dataset with custom camera configurations."""

    config = GenerationConfig(
        model_dir=Path("./models"),
        output_dir=Path("./output_custom_camera"),
        num_images=50,
    )

    # Configure for pure nadir (directly overhead) photography
    config.camera.nadir_angle_range = (0, 5)  # Nearly vertical
    config.camera.orbit_angles = 12  # 12 positions around the scene
    config.camera.distance_range = (0.9, 1.2)  # Closer range
    config.camera.resolution = (2048, 2048)  # Square images

    # Adjust lighting for overhead view
    config.lighting.num_lights = (3, 5)
    config.lighting.intensity_range = (800, 1800)

    # Generate dataset
    generator = SyntheticGenerator(config)
    generator.generate()

    print("Custom camera angle dataset generated!")


if __name__ == "__main__":
    main()
