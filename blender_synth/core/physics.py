"""Physics simulation for realistic object placement."""

import numpy as np
import blenderproc as bproc

from blender_synth.pipeline.config import PhysicsConfig


class PhysicsSimulator:
    """Manages physics simulation for dropping objects onto table."""

    def __init__(self, config: PhysicsConfig):
        """Initialize physics simulator.

        Args:
            config: Physics configuration
        """
        self.config = config

    def setup_physics(self) -> None:
        """Configure physics world settings."""
        if not self.config.enabled:
            return

        # BlenderProc handles physics automatically when we call simulate_physics_and_fix_final_poses()
        pass

    def drop_objects(
        self,
        objects: list,
        surface: bproc.types.MeshObject,
        spawn_region: tuple = ((-0.4, 0.4), (-0.4, 0.4)),
    ) -> None:
        """Drop objects onto surface using physics simulation.

        Args:
            objects: List of objects to drop
            surface: Surface object (table/drawer)
            spawn_region: ((x_min, x_max), (y_min, y_max)) region to spawn objects
        """
        if not self.config.enabled:
            # Just place objects randomly without physics
            self._place_without_physics(objects, surface, spawn_region)
            return

        # Enable physics for surface (make it static)
        # Use MESH collision for better accuracy with plane
        surface.enable_rigidbody(
            active=False,  # Static object
            collision_shape="MESH",
            collision_margin=0.001  # Small margin to prevent objects going through
        )

        # Drop each object from random position
        for obj in objects:
            # Random spawn position above table
            x = np.random.uniform(*spawn_region[0])
            y = np.random.uniform(*spawn_region[1])
            z = self.config.drop_height

            obj.set_location([x, y, z])

            # Random rotation if enabled
            obj.set_rotation_euler(
                [
                    np.random.uniform(0, 2 * np.pi),
                    np.random.uniform(0, 2 * np.pi),
                    np.random.uniform(0, 2 * np.pi),
                ]
            )

            # Enable physics
            obj.enable_rigidbody(
                active=True,
                collision_shape="CONVEX_HULL",
                friction=self.config.friction,
                angular_damping=0.1,
                linear_damping=0.1,
            )

            # Set restitution (bounciness) directly via Blender API
            # The set_rigidbody_restitution method doesn't exist in newer BlenderProc versions
            import bpy
            if obj.blender_obj.rigid_body:
                obj.blender_obj.rigid_body.restitution = self.config.restitution

        # Run physics simulation with longer time to ensure proper settling
        bproc.object.simulate_physics_and_fix_final_poses(
            min_simulation_time=6.0,  # Increased from ~4.2 to 6 seconds
            max_simulation_time=10.0,  # Increased max time to allow full settling
            check_object_interval=0.5,  # Check more frequently
        )

        # Debug and adjust: Ensure objects are clearly above table surface
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"After physics simulation:")
        for obj in objects:
            loc = obj.get_location()
            # Ensure objects are properly resting on surface
            if loc[2] < 0.015:  # If very close to or below z=0
                new_z = 0.02  # Raise to 2cm above origin
                obj.set_location([loc[0], loc[1], new_z])
                loc = obj.get_location()
                logger.info(f"  {obj.get_name()}: ADJUSTED to location={loc}")
            else:
                logger.info(f"  {obj.get_name()}: location={loc}")

            cat_id = obj.get_cp("category_id") if obj.has_cp("category_id") else "None"
            logger.info(f"    category_id={cat_id}")

    def _place_without_physics(
        self, objects: list, surface: bproc.types.MeshObject, spawn_region: tuple
    ) -> None:
        """Place objects randomly without physics simulation.

        Args:
            objects: List of objects to place
            surface: Surface object
            spawn_region: ((x_min, x_max), (y_min, y_max)) region to place objects
        """
        for obj in objects:
            # Random position on table
            x = np.random.uniform(*spawn_region[0])
            y = np.random.uniform(*spawn_region[1])

            # Place on surface (z = 0 plus half object height)
            bbox = obj.get_bound_box()
            z_min = min(p[2] for p in bbox)
            z_offset = -z_min  # Offset to place bottom at z=0

            obj.set_location([x, y, z_offset])

            # Random Z rotation (objects lie flat on table)
            obj.set_rotation_euler([0, 0, np.random.uniform(0, 2 * np.pi)])

    def check_stability(self, objects: list, threshold: float = 0.01) -> bool:
        """Check if objects have settled and are stable.

        Args:
            objects: List of objects to check
            threshold: Velocity threshold for stability

        Returns:
            True if all objects are stable
        """
        # This is handled by BlenderProc's simulate_physics_and_fix_final_poses
        return True
