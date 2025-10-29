import blenderproc as bproc

"""BlenderProc worker script that runs inside Blender's Python environment."""

import argparse
import sys
import json
from pathlib import Path
from datetime import datetime

# Add the package root to the Python path so blender_synth can be imported
# worker.py is in blender_synth/, so parent.parent is the package root
sys.path.insert(0, str(Path(__file__).parent.parent))

# This script runs inside blenderproc, so these imports are safe here
from blender_synth.pipeline.config import GenerationConfig
from blender_synth.pipeline.generator import SyntheticGenerator
from blender_synth.utils.logger import setup_logger, create_log_directory, setup_run_logger


def main():
    """Worker script main entry point - runs inside BlenderProc."""
    parser = argparse.ArgumentParser(description="BlenderProc worker script")
    parser.add_argument("--command", type=str, required=True, help="Command to execute (generate or preview)")
    parser.add_argument("--config", type=Path, help="Path to YAML configuration file")
    parser.add_argument("--models", type=Path, help="Directory containing 3D models")
    parser.add_argument("--output", type=Path, help="Output directory for dataset")
    parser.add_argument("--num-images", type=int, default=100, help="Number of images to generate")
    parser.add_argument("--camera-angles", type=int, default=8, help="Number of camera orbit positions")
    parser.add_argument("--max-objects", type=int, default=5, help="Maximum objects per scene")
    parser.add_argument("--resolution", type=int, nargs=2, default=[1920, 1080], help="Image resolution")
    parser.add_argument("--seed", type=int, help="Random seed for reproducibility")
    parser.add_argument("--no-physics", action="store_true", help="Disable physics simulation")
    parser.add_argument("--engine", choices=["CYCLES", "EEVEE"], default="CYCLES", help="Rendering engine")
    parser.add_argument("--samples", type=int, default=128, help="Number of render samples")

    args = parser.parse_args()

    # Use basic logger initially
    logger = setup_logger()

    try:
        if args.command == "generate":
            return generate_command(args, logger)
        elif args.command == "preview":
            return preview_command(args, logger)
        else:
            logger.error(f"Unknown command: {args.command}")
            return 1
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


def generate_command(args: argparse.Namespace, logger) -> int:
    """Execute generate command.

    Args:
        args: Parsed arguments
        logger: Logger instance

    Returns:
        Exit code
    """
    # Load or create configuration
    if args.config:
        logger.info(f"Loading configuration from {args.config}")
        config = GenerationConfig.from_yaml(args.config)
    else:
        # Create from command-line arguments
        if not args.models or not args.output:
            logger.error("--models and --output are required when not using --config")
            return 1

        config = GenerationConfig(
            model_dir=args.models,
            output_dir=args.output,
            num_images=args.num_images,
            random_seed=args.seed,
        )

        # Update with command-line overrides
        config.camera.orbit_angles = args.camera_angles
        config.camera.resolution = tuple(args.resolution)
        config.models.max_per_scene = args.max_objects
        config.physics.enabled = not args.no_physics
        config.rendering.engine = args.engine
        config.rendering.samples = args.samples

    # Create log directory for this run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = create_log_directory(Path(config.output_dir), run_type="generation", timestamp=timestamp)

    # Set up file logging
    logger = setup_run_logger(log_dir, run_type="generation")

    # Log run metadata
    _save_run_metadata(log_dir, args, config, "generation")

    # Create generator and run
    generator = SyntheticGenerator(config, logger=logger, log_dir=log_dir)
    generator.generate()

    logger.info(f"Run logs saved to: {log_dir}")
    return 0


def preview_command(args: argparse.Namespace, logger) -> int:
    """Execute preview command.

    Args:
        args: Parsed arguments
        logger: Logger instance

    Returns:
        Exit code
    """
    # Create minimal configuration
    config = GenerationConfig(
        model_dir=args.models,
        output_dir=args.output,
        num_images=args.num_images,
    )

    config.camera.orbit_angles = args.camera_angles

    # Create log directory for this preview run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = create_log_directory(Path(config.output_dir), run_type="preview", timestamp=timestamp)

    # Set up file logging
    logger = setup_run_logger(log_dir, run_type="preview")

    # Log run metadata
    _save_run_metadata(log_dir, args, config, "preview")

    # Create generator
    generator = SyntheticGenerator(config, logger=logger, log_dir=log_dir)
    generator.generate_preview(num_images=args.num_images)

    logger.info(f"Preview run logs saved to: {log_dir}")
    return 0


def _save_run_metadata(log_dir: Path, args: argparse.Namespace, config: GenerationConfig, command: str) -> None:
    """Save metadata about the run to a JSON file.

    Args:
        log_dir: Directory to save metadata to
        args: Command-line arguments
        config: Generation configuration
        command: Command type (generation/preview)
    """
    metadata = {
        "command": command,
        "timestamp": datetime.now().isoformat(),
        "arguments": {
            "models": str(args.models) if args.models else None,
            "output": str(args.output) if args.output else None,
            "num_images": args.num_images,
            "camera_angles": args.camera_angles,
            "max_objects": args.max_objects,
            "resolution": args.resolution,
            "seed": args.seed,
            "physics_enabled": not args.no_physics,
            "engine": args.engine,
            "samples": args.samples,
        },
        "config_file": str(args.config) if args.config else None,
    }

    metadata_path = log_dir / "run_metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)


if __name__ == "__main__":
    sys.exit(main())
