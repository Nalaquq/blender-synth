"""Configuration management for synthetic data generation."""

from pathlib import Path
from typing import Literal, Optional, Tuple

from pydantic import BaseModel, Field, field_validator


class CameraConfig(BaseModel):
    """Camera configuration for nadir/near-nadir photography."""

    nadir_angle_range: Tuple[float, float] = Field(
        default=(0, 15),
        description="Range of angles from vertical (degrees). 0 = pure nadir.",
    )
    orbit_angles: int = Field(
        default=8, description="Number of camera positions around the scene", ge=1
    )
    distance_range: Tuple[float, float] = Field(
        default=(0.8, 1.5), description="Camera distance from scene center (meters)"
    )
    resolution: Tuple[int, int] = Field(
        default=(1920, 1080), description="Output image resolution (width, height)"
    )
    focal_length: float = Field(
        default=50.0, description="Camera focal length (mm)", gt=0
    )

    @field_validator("nadir_angle_range", "distance_range")
    @classmethod
    def validate_range(cls, v: Tuple[float, float]) -> Tuple[float, float]:
        """Validate that min < max in ranges."""
        if v[0] >= v[1]:
            raise ValueError("Range minimum must be less than maximum")
        return v


class PhysicsConfig(BaseModel):
    """Physics simulation configuration."""

    enabled: bool = Field(default=True, description="Enable physics simulation")
    drop_height: float = Field(
        default=0.3, description="Height to drop objects from (meters)", ge=0
    )
    simulation_steps: int = Field(
        default=100, description="Number of physics simulation frames", ge=1
    )
    gravity: Tuple[float, float, float] = Field(
        default=(0, 0, -9.81), description="Gravity vector (m/s²)"
    )
    friction: float = Field(
        default=0.5, description="Object friction coefficient", ge=0, le=1
    )
    restitution: float = Field(
        default=0.3, description="Object bounciness", ge=0, le=1
    )


class LightingConfig(BaseModel):
    """Lighting randomization configuration."""

    num_lights: Tuple[int, int] = Field(
        default=(2, 4), description="Range of number of lights"
    )
    intensity_range: Tuple[float, float] = Field(
        default=(30, 100), description="Light intensity range (Watts)"
    )
    color_temp_range: Tuple[float, float] = Field(
        default=(3000, 6500), description="Color temperature range (Kelvin)"
    )
    use_hdri: bool = Field(
        default=False, description="Use HDRI environment lighting"
    )


class BackgroundConfig(BaseModel):
    """Background/drawer configuration."""

    use_drawer_texture: bool = Field(
        default=True, description="Use drawer-like background texture"
    )
    randomize_color: bool = Field(default=True, description="Randomize background color")
    color_variation: float = Field(
        default=0.2, description="Amount of color variation", ge=0, le=1
    )
    base_color: Tuple[float, float, float] = Field(
        default=(0.5, 0.48, 0.45), description="Base RGB color for drawer background"
    )


class RenderConfig(BaseModel):
    """Rendering configuration."""

    engine: Literal["CYCLES", "EEVEE"] = Field(
        default="CYCLES", description="Rendering engine"
    )
    samples: int = Field(default=128, description="Number of render samples", ge=1)
    max_bounces: int = Field(default=4, description="Maximum light bounces", ge=0)
    use_denoising: bool = Field(default=True, description="Enable denoising")
    use_gpu: bool = Field(
        default=True,
        description="Prefer GPU acceleration. Automatically detects and uses GPU if available, falls back to CPU if not. Set to False to force CPU rendering."
    )


class ModelConfig(BaseModel):
    """3D model configuration."""

    max_per_scene: int = Field(
        default=5, description="Maximum objects per scene", ge=1
    )
    min_per_scene: int = Field(
        default=1, description="Minimum objects per scene", ge=1
    )
    scale_range: Tuple[float, float] = Field(
        default=(0.8, 1.2), description="Object scale variation range"
    )
    randomize_rotation: bool = Field(
        default=True, description="Randomize object rotation"
    )

    @field_validator("min_per_scene")
    @classmethod
    def validate_min_max(cls, v: int, info) -> int:
        """Validate that min <= max."""
        if "max_per_scene" in info.data and v > info.data["max_per_scene"]:
            raise ValueError("min_per_scene must be <= max_per_scene")
        return v


class DatasetConfig(BaseModel):
    """Dataset split configuration."""

    train_split: float = Field(default=0.7, description="Training set ratio", ge=0, le=1)
    val_split: float = Field(default=0.15, description="Validation set ratio", ge=0, le=1)
    test_split: float = Field(default=0.15, description="Test set ratio", ge=0, le=1)

    @field_validator("test_split")
    @classmethod
    def validate_splits_sum_to_one(cls, v: float, info) -> float:
        """Validate that splits sum to 1.0."""
        total = v + info.data.get("train_split", 0) + info.data.get("val_split", 0)
        if not (0.99 <= total <= 1.01):  # Allow small floating point error
            raise ValueError(
                f"Dataset splits must sum to 1.0, got {total:.3f}"
            )
        return v


class GenerationConfig(BaseModel):
    """Main configuration for synthetic data generation."""

    # Required paths
    model_dir: Path = Field(description="Directory containing 3D models")
    output_dir: Path = Field(description="Output directory for generated dataset")

    # Generation parameters
    num_images: int = Field(
        default=100, description="Total number of images to generate", ge=1
    )
    random_seed: Optional[int] = Field(
        default=None, description="Random seed for reproducibility"
    )
    create_visualizations: bool = Field(
        default=False, description="Automatically create annotated visualization images after generation"
    )

    # Sub-configurations
    camera: CameraConfig = Field(default_factory=CameraConfig)
    physics: PhysicsConfig = Field(default_factory=PhysicsConfig)
    lighting: LightingConfig = Field(default_factory=LightingConfig)
    background: BackgroundConfig = Field(default_factory=BackgroundConfig)
    rendering: RenderConfig = Field(default_factory=RenderConfig)
    models: ModelConfig = Field(default_factory=ModelConfig)
    dataset: DatasetConfig = Field(default_factory=DatasetConfig)

    @field_validator("model_dir")
    @classmethod
    def validate_model_dir_exists(cls, v: Path) -> Path:
        """Validate that model directory exists."""
        if not v.exists():
            raise ValueError(f"Model directory does not exist: {v}")
        if not v.is_dir():
            raise ValueError(f"Model path is not a directory: {v}")
        return v

    def model_post_init(self, __context) -> None:
        """Create output directory if it doesn't exist."""
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_yaml(cls, path: Path) -> "GenerationConfig":
        """Load configuration from YAML file."""
        import yaml

        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data)

    def to_yaml(self, path: Path) -> None:
        """Save configuration to YAML file."""
        import yaml

        # Convert to dict and handle Path objects
        data = self.model_dump(mode="python")
        data["model_dir"] = str(data["model_dir"])
        data["output_dir"] = str(data["output_dir"])

        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
