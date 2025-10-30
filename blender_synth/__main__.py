"""Command-line interface for blender-synth."""

import argparse
import os
import subprocess
import sys
from pathlib import Path

from blender_synth.utils.logger import setup_logger


def setup_cuda_env() -> None:
    """Set up CUDA environment variables for GPU support."""
    cuda_paths = []
    current_ld_path = os.environ.get('LD_LIBRARY_PATH', '')

    # WSL2 CUDA libraries
    if os.path.isdir('/usr/lib/wsl/lib'):
        cuda_paths.append('/usr/lib/wsl/lib')

    # Standard CUDA installation
    if os.path.isdir('/usr/local/cuda/lib64'):
        cuda_paths.append('/usr/local/cuda/lib64')

    # Versioned CUDA installations
    for cuda_dir in sorted(Path('/usr/local').glob('cuda-*/targets/x86_64-linux/lib'), reverse=True):
        if cuda_dir.exists():
            cuda_paths.append(str(cuda_dir))
            break

    # Update LD_LIBRARY_PATH if CUDA paths found
    if cuda_paths:
        new_paths = cuda_paths + ([current_ld_path] if current_ld_path else [])
        os.environ['LD_LIBRARY_PATH'] = ':'.join(new_paths)


def main() -> int:
    """Main CLI entry point."""
    # Set up CUDA environment before launching blenderproc
    setup_cuda_env()

    parser = argparse.ArgumentParser(
        description="Generate synthetic datasets for archaeological artifact detection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate dataset with default settings
  blender-synth generate --models ./models --output ./output

  # Generate with custom settings
  blender-synth generate --models ./models --output ./output \\
      --num-images 1000 --camera-angles 12 --max-objects 8

  # Generate from config file
  blender-synth generate --config config.yaml

  # Generate preview for testing
  blender-synth preview --models ./models --output ./preview --num-images 10
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Generate command
    generate_parser = subparsers.add_parser(
        "generate", help="Generate synthetic dataset"
    )
    generate_parser.add_argument(
        "--models",
        type=Path,
        help="Directory containing 3D models organized by class",
    )
    generate_parser.add_argument(
        "--output", type=Path, help="Output directory for dataset"
    )
    generate_parser.add_argument(
        "--config", type=Path, help="Path to YAML configuration file"
    )
    generate_parser.add_argument(
        "--num-images", type=int, default=None, help="Number of images to generate (overrides config)"
    )
    generate_parser.add_argument(
        "--camera-angles",
        type=int,
        default=None,
        help="Number of camera orbit positions (overrides config)",
    )
    generate_parser.add_argument(
        "--max-objects",
        type=int,
        default=None,
        help="Maximum objects per scene (overrides config)",
    )
    generate_parser.add_argument(
        "--resolution",
        type=int,
        nargs=2,
        default=None,
        metavar=("WIDTH", "HEIGHT"),
        help="Image resolution (overrides config)",
    )
    generate_parser.add_argument(
        "--seed", type=int, default=None, help="Random seed for reproducibility (overrides config)"
    )
    generate_parser.add_argument(
        "--no-physics", action="store_true", help="Disable physics simulation (overrides config)"
    )
    generate_parser.add_argument(
        "--engine",
        choices=["CYCLES", "EEVEE"],
        default=None,
        help="Rendering engine (overrides config)",
    )
    generate_parser.add_argument(
        "--samples", type=int, default=None, help="Number of render samples (overrides config)"
    )

    # Preview command
    preview_parser = subparsers.add_parser(
        "preview", help="Generate preview images for testing"
    )
    preview_parser.add_argument(
        "--models", type=Path, required=True, help="Directory containing 3D models"
    )
    preview_parser.add_argument(
        "--output", type=Path, required=True, help="Output directory for preview"
    )
    preview_parser.add_argument(
        "--num-images", type=int, default=5, help="Number of preview images"
    )
    preview_parser.add_argument(
        "--camera-angles", type=int, default=8, help="Number of camera positions"
    )

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Set up logger
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
    """Execute generate command by invoking blenderproc worker.

    Args:
        args: Parsed arguments
        logger: Logger instance

    Returns:
        Exit code
    """
    # Validate required arguments
    if not args.config and (not args.models or not args.output):
        logger.error("--models and --output are required when not using --config")
        return 1

    # Build blenderproc command
    worker_script = Path(__file__).parent / "worker.py"
    cmd = ["blenderproc", "run", str(worker_script), "--command", "generate"]

    # Add all arguments (only pass if explicitly set to avoid overriding config defaults)
    if args.config:
        cmd.extend(["--config", str(args.config)])
    if args.models:
        cmd.extend(["--models", str(args.models)])
    if args.output:
        cmd.extend(["--output", str(args.output)])
    if args.num_images is not None:
        cmd.extend(["--num-images", str(args.num_images)])
    if args.camera_angles is not None:
        cmd.extend(["--camera-angles", str(args.camera_angles)])
    if args.max_objects is not None:
        cmd.extend(["--max-objects", str(args.max_objects)])
    if args.resolution is not None:
        cmd.extend(["--resolution", str(args.resolution[0]), str(args.resolution[1])])
    if args.seed is not None:
        cmd.extend(["--seed", str(args.seed)])
    if args.no_physics:
        cmd.append("--no-physics")
    if args.engine is not None:
        cmd.extend(["--engine", args.engine])
    if args.samples is not None:
        cmd.extend(["--samples", str(args.samples)])

    # Execute blenderproc
    logger.info("Launching BlenderProc worker...")
    logger.info(f"Command: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except FileNotFoundError:
        logger.error("blenderproc not found. Please ensure BlenderProc is installed: pip install blenderproc")
        return 1
    except Exception as e:
        logger.error(f"Failed to run blenderproc: {e}")
        return 1


def preview_command(args: argparse.Namespace, logger) -> int:
    """Execute preview command by invoking blenderproc worker.

    Args:
        args: Parsed arguments
        logger: Logger instance

    Returns:
        Exit code
    """
    # Build blenderproc command
    worker_script = Path(__file__).parent / "worker.py"
    cmd = ["blenderproc", "run", str(worker_script), "--command", "preview"]

    # Add all arguments
    cmd.extend(["--models", str(args.models)])
    cmd.extend(["--output", str(args.output)])
    cmd.extend(["--num-images", str(args.num_images)])
    cmd.extend(["--camera-angles", str(args.camera_angles)])

    # Execute blenderproc
    logger.info("Launching BlenderProc worker for preview...")
    logger.info(f"Command: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except FileNotFoundError:
        logger.error("blenderproc not found. Please ensure BlenderProc is installed: pip install blenderproc")
        return 1
    except Exception as e:
        logger.error(f"Failed to run blenderproc: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
