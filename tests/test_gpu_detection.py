import blenderproc as bproc
# Test script to verify GPU detection and configuration
import sys
from pathlib import Path

# Add blender_synth to path
sys.path.insert(0, str(Path(__file__).parent))

from blender_synth.utils.gpu import detect_gpu_devices, configure_gpu_rendering, get_device_info
from blender_synth.pipeline.config import RenderConfig
from blender_synth.core.scene import SceneManager
from blender_synth.pipeline.config import BackgroundConfig
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_gpu_detection():
    """Test GPU detection without initializing Blender."""
    logger.info("=" * 70)
    logger.info("Testing GPU Detection (requires Blender/BlenderProc context)")
    logger.info("=" * 70)

    # Test with GPU enabled
    logger.info("\nTest 1: GPU detection with use_gpu=True")
    render_config = RenderConfig(use_gpu=True)
    background_config = BackgroundConfig()
    scene_manager = SceneManager(render_config, background_config)

    logger.info("Initializing SceneManager with GPU enabled...")
    scene_manager.initialize()

    logger.info(f"GPU Usage Status: {scene_manager.is_using_gpu()}")
    logger.info(f"Device Info: {get_device_info()}")

    # Test with GPU disabled
    logger.info("\n" + "=" * 70)
    logger.info("Test 2: GPU detection with use_gpu=False")
    render_config_cpu = RenderConfig(use_gpu=False)
    scene_manager_cpu = SceneManager(render_config_cpu, BackgroundConfig())

    # Note: Can't initialize twice in same session, but we can test the config
    logger.info(f"Configuration set to use GPU: {render_config_cpu.use_gpu}")

    logger.info("\n" + "=" * 70)
    logger.info("GPU Detection Tests Complete")
    logger.info("=" * 70)


if __name__ == "__main__":
    test_gpu_detection()
