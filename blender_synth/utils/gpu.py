"""GPU detection and configuration utilities."""

import logging
from typing import Optional, List, Tuple

logger = logging.getLogger(__name__)


def detect_gpu_devices() -> Tuple[bool, List[str]]:
    """Detect available GPU devices for rendering.

    Returns:
        Tuple of (has_gpu, device_names) where:
        - has_gpu: True if any GPU devices are available
        - device_names: List of GPU device names
    """
    try:
        import bpy

        # Get compute device type preferences
        prefs = bpy.context.preferences
        cycles_prefs = prefs.addons.get('cycles')

        if cycles_prefs is None:
            logger.warning("Cycles addon not available")
            return False, []

        # Try different compute device types in order of preference
        # OPTIX is faster than CUDA for NVIDIA RTX cards
        device_types_to_try = ['OPTIX', 'CUDA', 'HIP', 'METAL', 'ONEAPI']

        best_devices = []
        best_device_type = None

        for device_type in device_types_to_try:
            try:
                # Try setting this compute device type
                cycles_prefs.preferences.compute_device_type = device_type
                cycles_prefs.preferences.get_devices()
                devices = cycles_prefs.preferences.devices

                # Check for GPU devices
                gpu_devices = []
                for device in devices:
                    if device.type != 'CPU':
                        gpu_devices.append(f"{device.name} ({device.type})")
                        logger.debug(f"Found GPU device with {device_type}: {device.name} ({device.type})")

                # If we found devices with this type, use it
                if gpu_devices:
                    best_devices = gpu_devices
                    best_device_type = device_type
                    logger.debug(f"Successfully configured {device_type} with {len(gpu_devices)} device(s)")
                    break  # Use the first working type (highest priority)

            except Exception as e:
                logger.debug(f"Could not configure {device_type}: {e}")
                continue

        has_gpu = len(best_devices) > 0

        if has_gpu:
            logger.info(f"Detected {len(best_devices)} GPU device(s) using {best_device_type}: {', '.join(best_devices)}")
        else:
            logger.info("No GPU devices detected for any compute device type")

        return has_gpu, best_devices

    except ImportError:
        logger.warning("bpy module not available - cannot detect GPU devices")
        return False, []
    except Exception as e:
        logger.warning(f"Error detecting GPU devices: {e}")
        return False, []


def configure_gpu_rendering(use_gpu_preference: bool = True) -> bool:
    """Configure rendering to use GPU if available and requested.

    Args:
        use_gpu_preference: User preference for GPU usage (default: True)

    Returns:
        bool: True if GPU will be used, False if CPU will be used
    """
    # First check if user wants to use GPU
    if not use_gpu_preference:
        logger.info("GPU rendering disabled by user configuration")
        return False

    # Detect available GPUs
    has_gpu, gpu_devices = detect_gpu_devices()

    if not has_gpu:
        logger.info("No GPU devices available - falling back to CPU rendering")
        return False

    # GPU is available and user wants to use it
    try:
        import bpy

        # Enable GPU devices
        prefs = bpy.context.preferences
        cycles_prefs = prefs.addons['cycles']
        cycles_prefs.preferences.get_devices()

        # Enable all GPU devices
        for device in cycles_prefs.preferences.devices:
            if device.type != 'CPU':
                device.use = True
                logger.debug(f"Enabled GPU device: {device.name}")

        logger.info(f"GPU rendering enabled with {len(gpu_devices)} device(s)")
        return True

    except Exception as e:
        logger.warning(f"Error configuring GPU rendering: {e}")
        logger.info("Falling back to CPU rendering")
        return False


def get_device_info() -> str:
    """Get a human-readable string describing the rendering device configuration.

    Returns:
        String describing the active rendering device(s)
    """
    has_gpu, gpu_devices = detect_gpu_devices()

    if not has_gpu:
        return "CPU"

    if len(gpu_devices) == 1:
        return f"GPU ({gpu_devices[0]})"
    else:
        return f"GPU ({len(gpu_devices)} devices: {', '.join(gpu_devices)})"
