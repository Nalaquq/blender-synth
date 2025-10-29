"""Logging utilities."""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


def setup_logger(
    name: str = "blender_synth",
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
    log_to_console: bool = True,
) -> logging.Logger:
    """Set up logger with consistent formatting.

    Args:
        name: Logger name
        level: Logging level
        log_file: Optional path to log file
        log_to_console: Whether to log to console (default: True)

    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove existing handlers
    logger.handlers.clear()

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File handler
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def create_log_directory(
    base_dir: Path,
    run_type: str = "generation",
    timestamp: Optional[str] = None,
) -> Path:
    """Create a timestamped log directory for a generation or test run.

    Args:
        base_dir: Base directory for logs (e.g., output_dir)
        run_type: Type of run (e.g., 'generation', 'preview', 'test')
        timestamp: Optional timestamp string, will be generated if not provided

    Returns:
        Path to the created log directory
    """
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    log_dir = base_dir / "logs" / f"{run_type}_{timestamp}"
    log_dir.mkdir(parents=True, exist_ok=True)

    return log_dir


def setup_run_logger(
    log_dir: Path,
    run_type: str = "generation",
    level: int = logging.INFO,
) -> logging.Logger:
    """Set up logger for a specific generation or test run.

    Creates both console and file handlers, with file output going to
    a log file in the specified log directory.

    Args:
        log_dir: Directory to store log files
        run_type: Type of run (used in log filename)
        level: Logging level

    Returns:
        Configured logger
    """
    log_file = log_dir / f"{run_type}.log"
    logger = setup_logger(
        name="blender_synth",
        level=level,
        log_file=log_file,
        log_to_console=True,
    )

    logger.info(f"Logging to: {log_file}")
    return logger
