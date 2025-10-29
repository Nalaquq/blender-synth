import blenderproc as bproc

"""Test annotation fix - generate just 2 images to verify labels work."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from blender_synth import SyntheticGenerator, GenerationConfig


def main():
    """Test annotation generation with fixes."""

    print("=" * 70)
    print("ANNOTATION FIX TEST - Generating 2 images")
    print("=" * 70)

    config = GenerationConfig(
        model_dir=Path("./models"),
        output_dir=Path("./annotation_test_output"),
        num_images=2,
        random_seed=42,
    )

    # Fast settings for quick test
    config.camera.orbit_angles = 1
    config.models.max_per_scene = 1
    config.models.min_per_scene = 1
    config.rendering.samples = 64  # Low samples for speed
    config.rendering.use_gpu = True

    generator = SyntheticGenerator(config)
    generator.generate()

    # Check results
    print("\n" + "=" * 70)
    print("Checking generated annotations...")
    print("=" * 70)

    label_dir = config.output_dir / "train" / "labels"
    for label_file in sorted(label_dir.glob("*.txt")):
        size = label_file.stat().st_size
        if size > 0:
            with open(label_file) as f:
                content = f.read()
            print(f"✓ {label_file.name}: {size} bytes - {len(content.splitlines())} annotations")
            print(f"  Content: {content[:100]}")
        else:
            print(f"✗ {label_file.name}: EMPTY")

    print("=" * 70)


if __name__ == "__main__":
    main()
