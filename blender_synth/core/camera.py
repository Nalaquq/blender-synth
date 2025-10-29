"""Camera setup and orbit control for nadir/near-nadir photography."""

import numpy as np
import blenderproc as bproc
from mathutils import Matrix, Vector

from blender_synth.pipeline.config import CameraConfig


class CameraOrbit:
    """Manages camera positioning for nadir/near-nadir overhead photography."""

    def __init__(self, config: CameraConfig):
        """Initialize camera orbit system.

        Args:
            config: Camera configuration
        """
        self.config = config
        self.camera_poses = []

    def setup_camera(self) -> None:
        """Set up camera with appropriate settings."""
        # Set camera intrinsics
        width, height = self.config.resolution
        bproc.camera.set_resolution(width, height)

        # Set focal length
        bproc.camera.set_intrinsics_from_blender_params(
            lens=self.config.focal_length,
            lens_unit="MILLIMETERS"
        )

    def generate_orbit_poses(
        self, scene_center: np.ndarray = np.array([0, 0, 0.15])
    ) -> list:
        """Generate camera poses in orbit around scene center.

        Creates camera positions that orbit around the scene at nadir or near-nadir
        angles, simulating overhead photography of a museum drawer.

        Args:
            scene_center: Center point to orbit around (typically above table surface)

        Returns:
            List of 4x4 camera pose matrices
        """
        poses = []

        # Generate orbit positions
        for i in range(self.config.orbit_angles):
            # Angle around the Z-axis (azimuth)
            azimuth = (2 * np.pi * i) / self.config.orbit_angles

            # Random distance from center
            distance = np.random.uniform(*self.config.distance_range)

            # Random nadir angle (angle from vertical)
            # 0 degrees = pure nadir (straight down)
            # 15 degrees = slight angle
            nadir_angle = np.random.uniform(*self.config.nadir_angle_range)
            nadir_angle_rad = np.radians(nadir_angle)

            # Calculate camera position
            # In nadir view, camera is above the scene looking down
            x = scene_center[0] + distance * np.sin(nadir_angle_rad) * np.cos(azimuth)
            y = scene_center[1] + distance * np.sin(nadir_angle_rad) * np.sin(azimuth)
            z = scene_center[2] + distance * np.cos(nadir_angle_rad)

            camera_location = np.array([x, y, z])

            # Create rotation matrix to look at scene center
            rotation_matrix = self._look_at_matrix(
                camera_location, scene_center, up=np.array([0, 1, 0])
            )

            # Combine into 4x4 transformation matrix
            pose = np.eye(4)
            pose[:3, :3] = rotation_matrix
            pose[:3, 3] = camera_location

            poses.append(pose)

        self.camera_poses = poses
        return poses

    def set_camera_pose(self, pose: np.ndarray) -> None:
        """Set camera to a specific pose.

        Args:
            pose: 4x4 transformation matrix
        """
        # Convert to BlenderProc format and set
        bproc.camera.add_camera_pose(pose)

    def set_random_pose(self) -> np.ndarray:
        """Set camera to a random pose from the generated orbits.

        Returns:
            The selected pose matrix
        """
        if not self.camera_poses:
            self.generate_orbit_poses()

        pose = self.camera_poses[np.random.randint(len(self.camera_poses))]
        self.set_camera_pose(pose)
        return pose

    def _look_at_matrix(
        self, camera_pos: np.ndarray, target_pos: np.ndarray, up: np.ndarray
    ) -> np.ndarray:
        """Create a rotation matrix for camera looking at target.

        Args:
            camera_pos: Camera position
            target_pos: Point to look at
            up: Up vector

        Returns:
            3x3 rotation matrix
        """
        # Calculate direction from camera to target
        forward = target_pos - camera_pos
        forward = forward / np.linalg.norm(forward)

        # Calculate right vector
        right = np.cross(forward, up)
        if np.linalg.norm(right) < 1e-6:
            # Handle case where forward and up are parallel
            up = np.array([0, 0, 1]) if abs(forward[2]) < 0.9 else np.array([1, 0, 0])
            right = np.cross(forward, up)
        right = right / np.linalg.norm(right)

        # Recalculate up vector to ensure orthogonality
        up = np.cross(right, forward)
        up = up / np.linalg.norm(up)

        # Create rotation matrix
        # In Blender, camera looks down -Z axis
        rotation = np.eye(3)
        rotation[:, 0] = right
        rotation[:, 1] = up
        rotation[:, 2] = -forward

        return rotation

    def get_scene_bounds(self, objects: list) -> tuple:
        """Calculate bounding box of all objects in scene.

        Args:
            objects: List of BlenderProc objects

        Returns:
            Tuple of (center, radius) where center is scene center and radius is
            distance to furthest point
        """
        if not objects:
            return np.array([0, 0, 0.15]), 0.5

        # Collect all vertices
        all_points = []
        for obj in objects:
            # Get object bounding box in world coordinates
            bbox_corners = obj.get_bound_box()
            all_points.extend(bbox_corners)

        all_points = np.array(all_points)

        # Calculate center and radius
        center = np.mean(all_points, axis=0)
        distances = np.linalg.norm(all_points - center, axis=1)
        radius = np.max(distances)

        return center, radius
