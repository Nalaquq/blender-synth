"""Lighting randomization for domain randomization."""

import numpy as np
import blenderproc as bproc

from blender_synth.pipeline.config import LightingConfig


class LightingRandomizer:
    """Randomizes lighting conditions for diverse training data."""

    def __init__(self, config: LightingConfig):
        """Initialize lighting randomizer.

        Args:
            config: Lighting configuration
        """
        self.config = config
        self.lights = []

    def clear_lights(self) -> None:
        """Remove all created lights."""
        for light in self.lights:
            light.delete()
        self.lights = []

    def create_random_lights(self, scene_center: np.ndarray = np.array([0, 0, 0.15])) -> None:
        """Create random lighting setup with guaranteed key light for proper shadows.

        Args:
            scene_center: Center of the scene to light
        """
        self.clear_lights()

        # Always add a key light for consistent illumination and shadows
        key_light = self._create_key_light(scene_center)
        self.lights.append(key_light)

        # Determine number of additional fill/accent lights
        num_additional_lights = np.random.randint(self.config.num_lights[0], self.config.num_lights[1])

        for i in range(num_additional_lights):
            # Random light type - prefer AREA and POINT for fill lighting
            light_type = np.random.choice(["POINT", "AREA", "SUN"], p=[0.4, 0.5, 0.1])

            # Random position around scene
            if light_type == "SUN":
                # Sun lights are directional, position doesn't matter much
                # But we set direction by pointing at scene center
                angle = np.random.uniform(0, 2 * np.pi)
                elevation = np.random.uniform(np.pi / 6, np.pi / 3)  # 30-60 degrees
                distance = 5  # Arbitrary, doesn't affect SUN

                x = scene_center[0] + distance * np.cos(angle) * np.sin(elevation)
                y = scene_center[1] + distance * np.sin(angle) * np.sin(elevation)
                z = scene_center[2] + distance * np.cos(elevation)
            else:
                # Point and area lights - position them around and above scene
                angle = np.random.uniform(0, 2 * np.pi)
                distance = np.random.uniform(0.5, 1.5)
                height = np.random.uniform(0.5, 1.5)

                x = scene_center[0] + distance * np.cos(angle)
                y = scene_center[1] + distance * np.sin(angle)
                z = scene_center[2] + height

            location = np.array([x, y, z])

            # Create light
            light = bproc.types.Light()
            light.set_type(light_type)
            light.set_location(location)

            # Random intensity (lower than key light for fill)
            intensity = np.random.uniform(self.config.intensity_range[0] * 0.5,
                                         self.config.intensity_range[1] * 0.6)
            light.set_energy(intensity)

            # Random color temperature
            color_temp = np.random.uniform(*self.config.color_temp_range)
            color = self._color_temperature_to_rgb(color_temp)
            light.set_color(color)

            # Point light at scene center
            direction = scene_center - location
            direction = direction / np.linalg.norm(direction)
            light.set_rotation_euler(self._direction_to_euler(direction))

            self.lights.append(light)

    def _create_key_light(self, scene_center: np.ndarray) -> bproc.types.Light:
        """Create a key light for primary illumination and shadows.

        Args:
            scene_center: Center of the scene to light

        Returns:
            The created key light
        """
        # Position key light at an angle that ensures good shadows
        # Typically from above and to the side at 30-45 degree angle
        angle = np.random.uniform(0, 2 * np.pi)
        elevation = np.radians(np.random.uniform(35, 55))  # 35-55 degrees elevation
        distance = np.random.uniform(1.0, 1.8)

        x = scene_center[0] + distance * np.cos(angle) * np.cos(elevation)
        y = scene_center[1] + distance * np.sin(angle) * np.cos(elevation)
        z = scene_center[2] + distance * np.sin(elevation)

        location = np.array([x, y, z])

        # Create AREA light for softer, more natural shadows
        light = bproc.types.Light()
        light.set_type("AREA")
        light.set_location(location)

        # Strong key light intensity
        intensity = np.random.uniform(self.config.intensity_range[1] * 0.8,
                                     self.config.intensity_range[1])
        light.set_energy(intensity)

        # Neutral to warm color temperature for key light
        color_temp = np.random.uniform(4500, 5500)
        color = self._color_temperature_to_rgb(color_temp)
        light.set_color(color)

        # Point light at scene center
        direction = scene_center - location
        direction = direction / np.linalg.norm(direction)
        light.set_rotation_euler(self._direction_to_euler(direction))

        return light

    def _color_temperature_to_rgb(self, kelvin: float) -> tuple:
        """Convert color temperature in Kelvin to RGB.

        Args:
            kelvin: Color temperature in Kelvin

        Returns:
            RGB tuple (values 0-1)
        """
        # Simplified color temperature to RGB conversion
        # Based on Tanner Helland's algorithm

        temp = kelvin / 100.0

        # Calculate red
        if temp <= 66:
            red = 1.0
        else:
            red = temp - 60
            red = 329.698727446 * (red ** -0.1332047592)
            red = max(0, min(1, red / 255.0))

        # Calculate green
        if temp <= 66:
            green = temp
            green = 99.4708025861 * np.log(green) - 161.1195681661
            green = max(0, min(1, green / 255.0))
        else:
            green = temp - 60
            green = 288.1221695283 * (green ** -0.0755148492)
            green = max(0, min(1, green / 255.0))

        # Calculate blue
        if temp >= 66:
            blue = 1.0
        elif temp <= 19:
            blue = 0.0
        else:
            blue = temp - 10
            blue = 138.5177312231 * np.log(blue) - 305.0447927307
            blue = max(0, min(1, blue / 255.0))

        return (red, green, blue)

    def _direction_to_euler(self, direction: np.ndarray) -> tuple:
        """Convert direction vector to Euler angles.

        Args:
            direction: Direction vector

        Returns:
            Euler angles (x, y, z) in radians
        """
        # Normalize direction
        direction = direction / np.linalg.norm(direction)

        # Calculate angles
        # This is a simplified version - may need adjustment
        pitch = np.arcsin(-direction[2])
        yaw = np.arctan2(direction[1], direction[0])
        roll = 0  # No roll for lights

        return (pitch, 0, yaw)
