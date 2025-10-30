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
    parser.add_argument("--num-images", type=int, default=None, help="Number of images to generate")
    parser.add_argument("--camera-angles", type=int, default=None, help="Number of camera orbit positions")
    parser.add_argument("--max-objects", type=int, default=None, help="Maximum objects per scene")
    parser.add_argument("--resolution", type=int, nargs=2, default=None, help="Image resolution")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")
    parser.add_argument("--no-physics", action="store_true", help="Disable physics simulation")
    parser.add_argument("--engine", choices=["CYCLES", "EEVEE"], default=None, help="Rendering engine")
    parser.add_argument("--samples", type=int, default=None, help="Number of render samples")

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

        # Apply command-line overrides only if explicitly provided
        if args.num_images is not None:
            config.num_images = args.num_images
        if args.seed is not None:
            config.random_seed = args.seed
        if args.camera_angles is not None:
            config.camera.orbit_angles = args.camera_angles
        if args.resolution is not None:
            config.camera.resolution = tuple(args.resolution)
        if args.max_objects is not None:
            config.models.max_per_scene = args.max_objects
        if args.no_physics:
            config.physics.enabled = False
        if args.engine is not None:
            config.rendering.engine = args.engine
        if args.samples is not None:
            config.rendering.samples = args.samples
    else:
        # Create from command-line arguments (use defaults if not provided)
        if not args.models or not args.output:
            logger.error("--models and --output are required when not using --config")
            return 1

        config = GenerationConfig(
            model_dir=args.models,
            output_dir=args.output,
            num_images=args.num_images if args.num_images is not None else 100,
            random_seed=args.seed,
        )

        # Update with command-line arguments or defaults
        config.camera.orbit_angles = args.camera_angles if args.camera_angles is not None else 8
        config.camera.resolution = tuple(args.resolution) if args.resolution is not None else (1920, 1080)
        config.models.max_per_scene = args.max_objects if args.max_objects is not None else 5
        config.physics.enabled = not args.no_physics
        config.rendering.engine = args.engine if args.engine is not None else "CYCLES"
        config.rendering.samples = args.samples if args.samples is not None else 128

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
