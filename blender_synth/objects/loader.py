"""3D model loading and management."""

from pathlib import Path
from typing import Dict, List
import numpy as np
import blenderproc as bproc

from blender_synth.pipeline.config import ModelConfig


class ModelLoader:
    """Loads and manages 3D models for synthetic data generation."""

    def __init__(self, model_dir: Path, config: ModelConfig):
        """Initialize model loader.

        Args:
            model_dir: Directory containing 3D models organized by class
            config: Model configuration
        """
        self.model_dir = Path(model_dir)
        self.config = config
        self.class_models: Dict[str, List[Path]] = {}
        self.class_names: List[str] = []
        self._instance_counter = 0  # Track unique instance IDs across all objects

    def discover_models(self) -> Dict[str, List[Path]]:
        """Discover 3D models organized in subdirectories.

        Expected structure:
            models/
                class1/
                    model1.obj
                    model2.glb
                class2/
                    model3.obj

        Returns:
            Dictionary mapping class names to lists of model paths
        """
        supported_formats = {".obj", ".glb", ".gltf", ".ply", ".stl", ".fbx"}

        class_models = {}

        # Iterate through subdirectories
        for class_dir in sorted(self.model_dir.iterdir()):
            if not class_dir.is_dir():
                continue

            class_name = class_dir.name
            models = []

            # Find all supported model files
            for model_file in class_dir.iterdir():
                if model_file.suffix.lower() in supported_formats:
                    models.append(model_file)

            if models:
                class_models[class_name] = sorted(models)

        self.class_models = class_models
        self.class_names = sorted(class_models.keys())

        return class_models

    def load_random_models(self, num_objects: int = None) -> List[bproc.types.MeshObject]:
        """Load random models from available classes.

        Args:
            num_objects: Number of objects to load. If None, uses random count
                        from config.

        Returns:
            List of loaded BlenderProc objects with class labels
        """
        if not self.class_models:
            self.discover_models()

        if not self.class_models:
            raise ValueError(f"No models found in {self.model_dir}")

        # Determine number of objects
        if num_objects is None:
            num_objects = np.random.randint(
                self.config.min_per_scene, self.config.max_per_scene + 1
            )

        loaded_objects = []

        for _ in range(num_objects):
            # Random class
            class_name = np.random.choice(self.class_names)
            class_idx = self.class_names.index(class_name)

            # Random model from class
            model_path = np.random.choice(self.class_models[class_name])

            # Load model
            objs = self._load_model(model_path)

            if not objs:
                import logging
                logging.warning(f"No mesh objects loaded from {model_path}")
                continue

            # Tag with class information
            for obj in objs:
                # Assign unique instance ID for each object
                self._instance_counter += 1

                obj.set_cp("class_name", class_name)
                obj.set_cp("class_id", class_idx)
                # Use class_idx + 1 as category_id (so it's not 0/background)
                # BlenderProc will handle instance IDs automatically
                obj.set_cp("category_id", class_idx + 1)

                # Random scale
                if self.config.scale_range != (1.0, 1.0):
                    scale = np.random.uniform(*self.config.scale_range)
                    obj.set_scale([scale, scale, scale])

                loaded_objects.append(obj)

        return loaded_objects

    def _load_model(self, model_path: Path) -> List[bproc.types.MeshObject]:
        """Load a 3D model file.

        Args:
            model_path: Path to model file

        Returns:
            List of loaded mesh objects
        """
        suffix = model_path.suffix.lower()

        if suffix == ".obj":
            objs = bproc.loader.load_obj(str(model_path))
        elif suffix in [".glb", ".gltf"]:
            # Use Blender's GLTF importer directly
            import bpy
            # Get existing objects before import
            existing_objs = set(bpy.data.objects)
            # Import GLTF
            bpy.ops.import_scene.gltf(filepath=str(model_path))
            # Get newly imported mesh objects
            new_objs = set(bpy.data.objects) - existing_objs
            objs = [bproc.types.MeshObject(obj) for obj in new_objs if obj.type == 'MESH']
        elif suffix == ".ply":
            objs = bproc.loader.load_ply(str(model_path))
        elif suffix == ".stl":
            # STL files need special handling
            objs = self._load_stl(model_path)
        else:
            # Generic import
            objs = bproc.loader.load_obj(str(model_path))

        return objs if isinstance(objs, list) else [objs]

    def _load_stl(self, model_path: Path) -> List[bproc.types.MeshObject]:
        """Load STL file (BlenderProc doesn't have native STL loader).

        Args:
            model_path: Path to STL file

        Returns:
            List containing loaded object
        """
        # Use Blender's operator through BlenderProc
        import bpy
        bpy.ops.import_mesh.stl(filepath=str(model_path))

        # Get the newly imported object
        imported_obj = bpy.context.selected_objects[0]
        return [bproc.types.MeshObject(imported_obj)]

    def get_class_names(self) -> List[str]:
        """Get list of class names.

        Returns:
            Sorted list of class names
        """
        if not self.class_names:
            self.discover_models()
        return self.class_names

    def get_num_classes(self) -> int:
        """Get number of classes.

        Returns:
            Number of distinct classes
        """
        return len(self.get_class_names())

    def reset_instance_counter(self) -> None:
        """Reset instance counter for new scene.

        Should be called before loading objects for each new image
        to ensure instance IDs start from 1 for each scene.
        """
        self._instance_counter = 0
