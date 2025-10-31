"""Scene setup and management using BlenderProc."""

import gc
import blenderproc as bproc
import numpy as np
import logging

from blender_synth.pipeline.config import BackgroundConfig, RenderConfig
from blender_synth.utils.gpu import configure_gpu_rendering, get_device_info

logger = logging.getLogger(__name__)


class SceneManager:
    """Manages BlenderProc scene setup and configuration."""

    def __init__(self, render_config: RenderConfig, background_config: BackgroundConfig):
        """Initialize scene manager.

        Args:
            render_config: Rendering configuration
            background_config: Background/drawer configuration
        """
        self.render_config = render_config
        self.background_config = background_config
        self._initialized = False
        self._using_gpu = False

    def initialize(self) -> None:
        """Initialize BlenderProc and set up basic scene."""
        if self._initialized:
            return

        # Initialize BlenderProc
        bproc.init()

        # Detect and configure GPU rendering
        self._using_gpu = configure_gpu_rendering(self.render_config.use_gpu)
        device_info = get_device_info()

        # Configure renderer
        if self.render_config.engine == "CYCLES":
            # Set render devices based on GPU detection result
            bproc.renderer.set_render_devices(use_only_cpu=not self._using_gpu)
            bproc.renderer.set_max_amount_of_samples(self.render_config.samples)
            bproc.renderer.set_light_bounces(
                max_bounces=self.render_config.max_bounces
            )
            if self.render_config.use_denoising:
                # Use OpenImageDenoise which is available in Blender 4.2
                bproc.renderer.set_denoiser("INTEL")
        else:
            # EEVEE settings
            bproc.renderer.set_render_devices(use_only_cpu=not self._using_gpu)

        # Log rendering configuration to user
        render_mode = "GPU" if self._using_gpu else "CPU"
        logger.info(f"Rendering with {self.render_config.engine} engine using {render_mode}")
        logger.info(f"Device: {device_info}")

        self._initialized = True

    def is_using_gpu(self) -> bool:
        """Check if GPU rendering is enabled.

        Returns:
            True if rendering with GPU, False if using CPU
        """
        return self._using_gpu

    def clear_scene(self) -> None:
        """Clear all objects from the scene and clean up Blender data blocks."""
        import bpy

        # Remove all mesh objects
        for obj in bproc.object.get_all_mesh_objects():
            obj.delete()

        # Clean up orphaned Blender data blocks to prevent memory leaks
        # This is critical when generating thousands of images
        self._cleanup_blender_data()

        # Force garbage collection to free memory immediately
        gc.collect()

    def _cleanup_blender_data(self) -> None:
        """Clean up orphaned Blender data blocks to prevent memory leaks.

        When objects are deleted, their associated data (meshes, materials, textures, images)
        may remain in Blender's memory. This method removes orphaned data blocks.
        """
        import bpy

        # Clean up orphaned meshes
        for mesh in bpy.data.meshes:
            if mesh.users == 0:
                bpy.data.meshes.remove(mesh)

        # Clean up orphaned materials
        for material in bpy.data.materials:
            if material.users == 0:
                bpy.data.materials.remove(material)

        # Clean up orphaned textures
        for texture in bpy.data.textures:
            if texture.users == 0:
                bpy.data.textures.remove(texture)

        # Clean up orphaned images (textures often reference images)
        for image in bpy.data.images:
            if image.users == 0:
                bpy.data.images.remove(image)

        # Clean up orphaned node groups (shader nodes can create these)
        for node_group in bpy.data.node_groups:
            if node_group.users == 0:
                bpy.data.node_groups.remove(node_group)

    def create_drawer_surface(self) -> bproc.types.MeshObject:
        """Create a table/drawer surface for objects to rest on.

        Returns:
            The created surface plane object
        """
        # Create a large plane for the drawer bottom
        # Increased size to catch objects better (3x3 instead of 2x2)
        # Place it slightly below z=0 so objects land ON TOP at z~0
        plane = bproc.object.create_primitive("PLANE", scale=[3, 3, 1])
        plane.set_location([0, 0, -0.01])  # Slightly below origin
        plane.set_name("drawer_surface")

        # Explicitly mark as background (category_id = 0) so it doesn't appear in segmentation
        plane.set_cp("category_id", 0)

        # Create material for drawer
        mat = plane.new_material("drawer_material")

        if self.background_config.use_drawer_texture:
            # Create wood-like or drawer-like appearance
            self._setup_drawer_material(mat)
        else:
            # Simple colored surface
            base_color = self.background_config.base_color
            if self.background_config.randomize_color:
                # Add some color variation
                variation = self.background_config.color_variation
                color = tuple(
                    max(0, min(1, c + np.random.uniform(-variation, variation)))
                    for c in base_color
                )
            else:
                color = base_color

            mat.set_principled_shader_value("Base Color", (*color, 1.0))
            mat.set_principled_shader_value("Roughness", 0.7)

        return plane

    def _setup_drawer_material(self, material: bproc.types.Material) -> None:
        """Set up a drawer/wood-like material.

        Args:
            material: Material to configure
        """
        # Base color with some variation
        base_color = self.background_config.base_color

        if self.background_config.randomize_color:
            variation = self.background_config.color_variation
            color = tuple(
                max(0, min(1, c + np.random.uniform(-variation, variation)))
                for c in base_color
            )
        else:
            color = base_color

        # Wood-like properties
        material.set_principled_shader_value("Base Color", (*color, 1.0))
        material.set_principled_shader_value("Roughness", np.random.uniform(0.5, 0.8))
        # Note: In Blender 4.0+, "Specular" was renamed to "Specular IOR Level"
        # For compatibility, we'll skip this or use a try-except
        try:
            material.set_principled_shader_value("Specular IOR Level", np.random.uniform(0.2, 0.4))
        except KeyError:
            pass  # Skip if not available

    def setup_world_lighting(self, use_hdri: bool = False) -> None:
        """Set up world/environment lighting.

        Args:
            use_hdri: Whether to use HDRI environment map
        """
        if use_hdri:
            # Would load HDRI here if available
            # For now, use simple world lighting
            pass

        # Set simple background color
        bproc.world.set_world_background_hdr_img(
            None, strength=0.5
        )  # No HDRI, just ambient
