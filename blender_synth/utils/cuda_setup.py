"""CUDA environment setup utilities for GPU support.

IMPORTANT: This module must be imported BEFORE blenderproc to properly set up
the environment for GPU detection.
"""

import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def setup_cuda_environment() -> bool:
    """Set up CUDA library paths for GPU support.

    This function should be called before importing blenderproc to ensure
    GPU devices can be detected. It adds common CUDA library paths to
    LD_LIBRARY_PATH.

    Returns:
        bool: True if any CUDA paths were added, False otherwise
    """
    cuda_paths = []
    current_ld_path = os.environ.get('LD_LIBRARY_PATH', '')

    # WSL2 CUDA libraries (nvidia-docker passthrough)
    wsl_cuda = Path('/usr/lib/wsl/lib')
    if wsl_cuda.exists():
        cuda_paths.append(str(wsl_cuda))
        logger.debug(f"Found WSL CUDA libraries: {wsl_cuda}")

    # Standard CUDA installation
    cuda_lib64 = Path('/usr/local/cuda/lib64')
    if cuda_lib64.exists():
        cuda_paths.append(str(cuda_lib64))
        logger.debug(f"Found CUDA libraries: {cuda_lib64}")

    # Versioned CUDA installations (e.g., cuda-11.8, cuda-12.4)
    cuda_base = Path('/usr/local')
    if cuda_base.exists():
        for cuda_dir in sorted(cuda_base.glob('cuda-*/targets/x86_64-linux/lib'), reverse=True):
            if cuda_dir.exists():
                cuda_paths.append(str(cuda_dir))
                logger.debug(f"Found versioned CUDA libraries: {cuda_dir}")
                break  # Use the newest version

    # Update LD_LIBRARY_PATH
    if cuda_paths:
        # Add new paths at the beginning
        new_paths = cuda_paths + ([current_ld_path] if current_ld_path else [])
        new_ld_path = ':'.join(new_paths)
        os.environ['LD_LIBRARY_PATH'] = new_ld_path

        logger.info(f"Added CUDA library paths: {', '.join(cuda_paths)}")
        return True
    else:
        logger.debug("No CUDA library paths found")
        return False


def check_cuda_available() -> bool:
    """Check if CUDA libraries are available in LD_LIBRARY_PATH.

    Returns:
        bool: True if CUDA libraries are in the path
    """
    ld_path = os.environ.get('LD_LIBRARY_PATH', '')

    cuda_indicators = [
        '/usr/lib/wsl/lib',
        '/usr/local/cuda',
        'cuda-',
    ]

    for indicator in cuda_indicators:
        if indicator in ld_path:
            return True

    return False


# Automatically set up CUDA environment when this module is imported
# (but only if blenderproc hasn't been imported yet)
if 'blenderproc' not in dir():
    setup_cuda_environment()
