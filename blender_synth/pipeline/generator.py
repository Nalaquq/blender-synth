"""Main synthetic data generation pipeline."""

import gc
import random
from pathlib import Path
from typing import List, Optional
import numpy as np
from tqdm import tqdm
import blenderproc as bproc

from blender_synth.pipeline.config import GenerationConfig
from blender_synth.core.scene import SceneManager
from blender_synth.core.camera import CameraOrbit
from blender_synth.core.physics import PhysicsSimulator
from blender_synth.objects.loader import ModelLoader
from blender_synth.randomization.lighting import LightingRandomizer
from blender_synth.annotation.yolo import YOLOAnnotator
from blender_synth.utils.logger import setup_logger


class SyntheticGenerator:
    """Main class for generating synthetic training datasets."""

    def __init__(self, config: GenerationConfig, logger=None, log_dir: Optional[Path] = None):
        """Initialize synthetic data generator.

        Args:
            config: Generation configuration
            logger: Optional logger instance (will create one if not provided)
            log_dir: Optional directory for storing logs
        """
        self.config = config
        self.logger = logger if logger is not None else setup_logger()
        self.log_dir = log_dir

        # Set random seeds
        if config.random_seed is not None:
            random.seed(config.random_seed)
            np.random.seed(config.random_seed)

        # Initialize components
        self.scene_manager = SceneManager(config.rendering, config.background)
        self.camera_orbit = CameraOrbit(config.camera)
        self.physics_sim = PhysicsSimulator(config.physics)
        self.model_loader = ModelLoader(config.model_dir, config.models)
        self.lighting = LightingRandomizer(config.lighting)

        # Annotation generator
        width, height = config.camera.resolution
        self.annotator = YOLOAnnotator(width, height)

        # Output directories
        self.output_dir = Path(config.output_dir)
        self.train_dir = self.output_dir / "train"
        self.val_dir = self.output_dir / "val"
        self.test_dir = self.output_dir / "test"

        # Clear output directory if requested
        if config.clear_output_dir:
            self._clear_output_directory()

        # Create output structure
        self._create_output_structure()

        # Track starting indices for each split when appending
        self._train_start_idx = self._get_next_index(self.train_dir / "images", "train")
        self._val_start_idx = self._get_next_index(self.val_dir / "images", "val")
        self._test_start_idx = self._get_next_index(self.test_dir / "images", "test")

        # Discover models
        self.logger.info(f"Discovering models in {config.model_dir}")
        self.model_loader.discover_models()
        self.logger.info(
            f"Found {self.model_loader.get_num_classes()} classes with models"
        )

        # Track memory usage
        self._images_generated = 0
        self._last_memory_log = 0
        self._peak_memory_mb = 0
        self._memory_log_entries = []  # Store memory metrics for CSV export

    def _aggressive_memory_cleanup(self) -> None:
        """Perform aggressive memory cleanup to prevent accumulation.

        This method clears caches and forces multiple garbage collection passes.
        Safe for background rendering (no UI operations).
        """
        import bpy

        # Clear active object reference
        try:
            if bpy.context.view_layer.objects.active:
                bpy.context.view_layer.objects.active = None
        except:
            pass  # May fail in background mode

        # Clear window manager caches if available
        # Note: Some operations may not work in background mode
        try:
            # Try to clear any cached data
            if hasattr(bpy.data, 'orphans_purge'):
                # Blender 2.9+ has orphans_purge which safely removes unused data
                bpy.data.orphans_purge()
        except:
            pass

        # Multiple garbage collection passes
        # First pass: collect objects with circular references
        gc.collect()
        # Second pass: collect objects that became eligible after first pass
        gc.collect()
        # Third pass: ensure everything is cleaned
        gc.collect()

    def _log_memory_usage(self, force: bool = False) -> None:
        """Log current memory usage and track peak usage.

        Args:
            force: Force logging regardless of interval
        """
        # Log more frequently for first 100 images to monitor memory leak fix
        # Then log every 50 images thereafter
        if self._images_generated < 100:
            interval = 10
        else:
            interval = 50

        # Always track memory even if we don't log it
        should_log = force or (self._images_generated - self._last_memory_log) >= interval

        try:
            import psutil
            import time
            process = psutil.Process()
            mem_info = process.memory_info()
            mem_mb = mem_info.rss / 1024 / 1024
            mem_gb = mem_mb / 1024

            # Track peak memory
            if mem_mb > self._peak_memory_mb:
                self._peak_memory_mb = mem_mb

            # Get Blender's internal data block counts for debugging
            import bpy
            mesh_count = len(bpy.data.meshes)
            material_count = len(bpy.data.materials)
            texture_count = len(bpy.data.textures)
            image_count = len(bpy.data.images)

            # Store metrics for CSV export
            self._memory_log_entries.append({
                'timestamp': time.time(),
                'images_generated': self._images_generated,
                'memory_mb': mem_mb,
                'memory_gb': mem_gb,
                'meshes': mesh_count,
                'materials': material_count,
                'textures': texture_count,
                'images': image_count
            })

            # Log to console and file
            if should_log:
                self.logger.info(
                    f"Memory: {mem_gb:.2f} GB ({mem_mb:.0f} MB) | "
                    f"Images: {self._images_generated} | "
                    f"Peak: {self._peak_memory_mb/1024:.2f} GB | "
                    f"Blender data blocks - Meshes: {mesh_count}, Materials: {material_count}, "
                    f"Textures: {texture_count}, Images: {image_count}"
                )
                self._last_memory_log = self._images_generated
        except ImportError:
            # psutil not available, skip memory logging
            pass

    def _clear_output_directory(self) -> None:
        """Clear the output directory completely."""
        import shutil

        if self.output_dir.exists():
            self.logger.info(f"Clearing output directory: {self.output_dir}")
            shutil.rmtree(self.output_dir)
            self.logger.info("Output directory cleared")

    def _get_next_index(self, images_dir: Path, split_name: str) -> int:
        """Get the next available index for image naming when appending.

        Args:
            images_dir: Directory containing existing images
            split_name: Name of the split (train/val/test)

        Returns:
            Next available index to use for image naming
        """
        if not images_dir.exists():
            return 0

        # Find all existing images for this split
        existing_images = list(images_dir.glob(f"{split_name}_*.jpg"))

        if not existing_images:
            return 0

        # Extract indices from filenames
        indices = []
        for img_path in existing_images:
            # Filename format: {split_name}_{index:06d}.jpg
            try:
                filename = img_path.stem  # Remove .jpg
                index_str = filename.split('_')[-1]  # Get the last part after underscore
                indices.append(int(index_str))
            except (ValueError, IndexError):
                # Skip files that don't match expected format
                continue

        if indices:
            next_idx = max(indices) + 1
            self.logger.info(f"Appending to existing {split_name} dataset. Starting at index {next_idx}")
            return next_idx

        return 0

    def _create_output_structure(self) -> None:
        """Create output directory structure."""
        for split_dir in [self.train_dir, self.val_dir, self.test_dir]:
            (split_dir / "images").mkdir(parents=True, exist_ok=True)
            (split_dir / "labels").mkdir(parents=True, exist_ok=True)

    def generate(self) -> None:
        """Generate synthetic dataset."""
        import time
        start_time = time.time()

        self.logger.info("Starting synthetic data generation")
        self.logger.info(f"Configuration: {self.config.num_images} images total")

        # Initialize BlenderProc
        self.logger.info("Initializing BlenderProc")
        self.scene_manager.initialize()

        # Notify user of rendering device
        device_type = "GPU" if self.scene_manager.is_using_gpu() else "CPU"
        self.logger.info(f"=" * 60)
        self.logger.info(f"RENDERING MODE: {device_type}")
        self.logger.info(f"=" * 60)

        self.camera_orbit.setup_camera()

        # Enable output types (normals and depth can be called once)
        bproc.renderer.enable_normals_output()
        bproc.renderer.enable_depth_output(activate_antialiasing=False)
        # NOTE: Segmentation output must be enabled AFTER objects are loaded in each scene
        # See _generate_single_image() for segmentation setup

        # Log initial memory usage as baseline
        self.logger.info("Initial memory usage:")
        self._log_memory_usage(force=True)

        # Calculate split sizes
        num_train = int(self.config.num_images * self.config.dataset.train_split)
        num_val = int(self.config.num_images * self.config.dataset.val_split)
        num_test = self.config.num_images - num_train - num_val

        self.logger.info(f"Dataset split - Train: {num_train}, Val: {num_val}, Test: {num_test}")

        # Generate splits
        self._generate_split("train", num_train, self.train_dir, self._train_start_idx)
        self._generate_split("val", num_val, self.val_dir, self._val_start_idx)
        self._generate_split("test", num_test, self.test_dir, self._test_start_idx)

        # Save class names
        self._save_class_names()

        # Save configuration
        self.config.to_yaml(self.output_dir / "config.yaml")

        # Create visualizations if requested
        if self.config.create_visualizations:
            self.logger.info("Creating annotation visualizations...")
            self._create_visualizations()

        # Log completion statistics
        elapsed_time = time.time() - start_time

        # Final memory log
        self._log_memory_usage(force=True)

        self.logger.info(f"=" * 60)
        self.logger.info(f"Generation complete! Dataset saved to {self.output_dir}")
        self.logger.info(f"Total time: {elapsed_time:.2f} seconds ({elapsed_time/60:.2f} minutes)")
        self.logger.info(f"Average time per image: {elapsed_time/self.config.num_images:.2f} seconds")
        self.logger.info(f"Peak memory usage: {self._peak_memory_mb/1024:.2f} GB ({self._peak_memory_mb:.0f} MB)")
        self.logger.info(f"=" * 60)

        # Save generation summary to log directory if available
        if self.log_dir:
            self._save_generation_summary(elapsed_time)
            self._save_memory_log_csv()

    def _generate_split(self, split_name: str, num_images: int, output_dir: Path, start_idx: int = 0) -> None:
        """Generate images for a dataset split.

        Args:
            split_name: Name of split (train/val/test)
            num_images: Number of images to generate
            output_dir: Output directory for this split
            start_idx: Starting index for image naming (for appending to existing dataset)
        """
        if start_idx > 0:
            self.logger.info(f"Generating {num_images} images for {split_name} split (starting from index {start_idx})")
        else:
            self.logger.info(f"Generating {num_images} images for {split_name} split")

        for i in tqdm(range(num_images), desc=f"Generating {split_name}"):
            # Generate single image with proper index
            image_idx = start_idx + i
            image_name = f"{split_name}_{image_idx:06d}"
            self._generate_single_image(image_name, output_dir)

    def _generate_single_image(self, image_name: str, output_dir: Path) -> None:
        """Generate a single annotated image with validation and retry logic.

        Args:
            image_name: Name for the image (without extension)
            output_dir: Output directory
        """
        max_retries = 5
        for attempt in range(max_retries):
            try:
                success = self._attempt_generate_image(image_name, output_dir)
                if success:
                    return
                else:
                    self.logger.warning(f"Attempt {attempt + 1}/{max_retries}: No valid annotations generated, retrying...")
            except Exception as e:
                self.logger.error(f"Attempt {attempt + 1}/{max_retries} failed with error: {e}")

        # If all retries failed, log error but continue (to not block entire generation)
        self.logger.error(f"Failed to generate valid image {image_name} after {max_retries} attempts")

    def _attempt_generate_image(self, image_name: str, output_dir: Path) -> bool:
        """Attempt to generate a single image. Returns True if successful with valid annotations.

        Args:
            image_name: Name for the image (without extension)
            output_dir: Output directory

        Returns:
            True if image was generated with valid annotations, False otherwise
        """
        # Clear scene
        self.scene_manager.clear_scene()
        self.lighting.clear_lights()

        # Create table surface
        surface = self.scene_manager.create_drawer_surface()

        # Reset instance counter for this new scene
        self.model_loader.reset_instance_counter()

        # Load random objects
        objects = self.model_loader.load_random_models()

        # Log loaded objects for debugging
        self.logger.info(f"Loaded {len(objects)} objects for this scene")
        for idx, obj in enumerate(objects):
            cat_id = obj.get_cp("category_id") if obj.has_cp("category_id") else "None"
            class_name = obj.get_cp("class_name") if obj.has_cp("class_name") else "Unknown"
            self.logger.info(f"  Object {idx}: {obj.get_name()}, class={class_name}, category_id={cat_id}")

        # Drop objects onto table with physics
        self.physics_sim.drop_objects(objects, surface)

        # Verify objects are still on the surface and in reasonable positions
        valid_objects = []
        for obj in objects:
            loc = obj.get_location()
            # Check if object is on the surface (z > 0) and within reasonable bounds
            if loc[2] > 0 and abs(loc[0]) < 1.0 and abs(loc[1]) < 1.0:
                valid_objects.append(obj)
            else:
                self.logger.warning(f"Object {obj.get_name()} fell off surface at location {loc}, removing from scene")
                obj.delete()

        if len(valid_objects) == 0:
            self.logger.warning("No objects remained on surface after physics simulation")
            return False

        objects = valid_objects

        # Set up random lighting (improved)
        # Aim slightly above table surface where objects are
        scene_center = np.array([0, 0, 0.05])
        self.lighting.create_random_lights(scene_center)

        # Set random camera pose
        self.camera_orbit.generate_orbit_poses(scene_center)
        self.camera_orbit.set_random_pose()

        # Enable segmentation output AFTER objects are loaded
        # This must be done for each scene because BlenderProc needs to know about
        # the objects that exist at render time
        bproc.renderer.enable_segmentation_output(
            map_by=["instance"],  # Use instance-based segmentation
            default_values={"category_id": 0}  # Default for objects without category_id
        )

        # Render
        data = bproc.renderer.render()

        # Generate annotations from segmentation BEFORE saving
        annotations = self._generate_annotations_from_data(data, objects)

        # Validate that we got annotations
        if len(annotations) == 0:
            self.logger.warning("No annotations generated - objects not visible in render")
            # Clean up render data even on failure - clear all components
            if 'colors' in data:
                del data['colors']
            if 'normals' in data:
                del data['normals']
            if 'depth' in data:
                del data['depth']
            if 'instance_segmaps' in data:
                del data['instance_segmaps']
            if 'instance_attribute_maps' in data:
                del data['instance_attribute_maps']
            del data
            gc.collect()
            return False

        # Only save if we have valid annotations
        # Save rendered image
        from PIL import Image
        image_path = output_dir / "images" / f"{image_name}.jpg"
        image_data = data["colors"][0]  # Get first camera view
        # Convert from float [0,1] to uint8 [0,255] if necessary
        if image_data.dtype == np.float32 or image_data.dtype == np.float64:
            image_data = (image_data * 255).astype(np.uint8)
        Image.fromarray(image_data).save(str(image_path), quality=95)

        # Save annotations
        label_path = output_dir / "labels" / f"{image_name}.txt"
        self.annotator.save_annotations(annotations, label_path)

        self.logger.info(f"Successfully generated {image_name} with {len(annotations)} annotations")

        # Free memory: explicitly delete large render data and force garbage collection
        # Clear all components of render data dict to ensure no references remain
        if 'colors' in data:
            del data['colors']
        if 'normals' in data:
            del data['normals']
        if 'depth' in data:
            del data['depth']
        if 'instance_segmaps' in data:
            del data['instance_segmaps']
        if 'instance_attribute_maps' in data:
            del data['instance_attribute_maps']

        del data
        del image_data
        gc.collect()

        # Update counter and log memory usage periodically
        self._images_generated += 1
        self._log_memory_usage()

        # Aggressive memory cleanup every 10 images to prevent accumulation
        if self._images_generated % 10 == 0:
            self._aggressive_memory_cleanup()

        return True

    def _generate_annotations_from_data(
        self, render_data: dict, objects: List
    ) -> List[str]:
        """Generate YOLO annotations from render data.

        Args:
            render_data: Rendered data from BlenderProc
            objects: List of objects in scene

        Returns:
            List of YOLO format annotation strings
        """
        annotations = []

        # Use instance_segmaps which assigns sequential IDs to objects
        seg_data = render_data.get("instance_segmaps", [None])[0]

        if seg_data is None:
            self.logger.warning(f"No instance segmentation data available")
            return annotations

        # Debug: Check segmentation map details
        self.logger.info(f"Segmentation map shape: {seg_data.shape}")
        self.logger.info(f"Segmentation map dtype: {seg_data.dtype}")
        self.logger.info(f"Segmentation map min/max: {seg_data.min()}/{seg_data.max()}")

        # Get unique instance IDs in the segmentation map (excluding background 0)
        unique_instances = np.unique(seg_data)
        self.logger.info(f"All unique values in segmentation (including background): {unique_instances}")
        unique_instances = unique_instances[unique_instances > 0]  # Remove background

        self.logger.info(f"Found {len(unique_instances)} instances in segmentation: {unique_instances}")
        self.logger.info(f"Have {len(objects)} objects to annotate")

        # Debug: Check if instance_attribute_maps exists
        if "instance_attribute_maps" in render_data:
            attr_map = render_data["instance_attribute_maps"][0]
            unique_attrs = np.unique(attr_map)
            self.logger.info(f"Instance attribute map unique values: {unique_attrs}")
        else:
            self.logger.warning("No instance_attribute_maps in render data!")

        # BlenderProc assigns instance IDs sequentially to ALL mesh objects in the scene
        # Instance 1 is the surface/plane (with category_id=0)
        # Instances 2+ are our target objects in the order they were added

        # Filter out the surface (instance 1) and match remaining instances to objects
        target_instances = [inst for inst in unique_instances if inst > 1]

        if len(target_instances) != len(objects):
            self.logger.warning(
                f"Mismatch: found {len(target_instances)} target instances but have {len(objects)} objects"
            )

        # Match instances to objects by order (instance 2 -> objects[0], instance 3 -> objects[1], etc.)
        for idx, obj in enumerate(objects):
            # Calculate instance ID (objects start at instance 2, after the surface at instance 1)
            instance_id = idx + 2

            if instance_id not in unique_instances:
                self.logger.warning(f"Object {idx} (expected instance {instance_id}) not found in segmentation")
                continue

            # Get mask for this instance
            mask = seg_data == instance_id

            if not mask.any():
                self.logger.warning(f"No pixels found for instance {instance_id}")
                continue

            # Convert mask to bbox
            bbox = self.annotator._mask_to_bbox(mask)

            if bbox is None:
                self.logger.warning(f"Invalid bbox for instance {instance_id}")
                continue

            # Get class ID from object
            class_id = obj.get_cp("class_id")

            # Convert to YOLO format
            yolo_annotation = self.annotator.bbox_to_yolo_format(bbox, class_id)
            annotations.append(yolo_annotation)
            self.logger.info(f"Generated annotation for instance {instance_id}, class {class_id}: {yolo_annotation}")

        return annotations

    def _save_class_names(self) -> None:
        """Save class names to file."""
        class_names = self.model_loader.get_class_names()

        classes_path = self.output_dir / "classes.txt"
        with open(classes_path, "w") as f:
            f.write("\n".join(class_names))

        self.logger.info(f"Saved {len(class_names)} class names to {classes_path}")

    def _create_visualizations(self) -> None:
        """Create annotated visualization images for all splits."""
        try:
            import cv2
        except ImportError:
            self.logger.warning(
                "opencv-python not installed. Skipping visualizations. "
                "Install with: pip install opencv-python"
            )
            return

        # Load class names
        classes_path = self.output_dir / "classes.txt"
        if classes_path.exists():
            with open(classes_path) as f:
                class_names = [line.strip() for line in f]
        else:
            class_names = None

        # Create visualizations for each split
        for split_name, split_dir in [("train", self.train_dir),
                                       ("val", self.val_dir),
                                       ("test", self.test_dir)]:
            images_dir = split_dir / "images"
            labels_dir = split_dir / "labels"
            vis_dir = self.output_dir / "visualizations" / split_name

            if not images_dir.exists():
                continue

            vis_dir.mkdir(parents=True, exist_ok=True)

            image_files = sorted(images_dir.glob("*.jpg"))
            if not image_files:
                continue

            self.logger.info(f"Creating visualizations for {len(image_files)} {split_name} images...")

            for img_path in image_files:
                label_path = labels_dir / f"{img_path.stem}.txt"
                output_path = vis_dir / f"{img_path.stem}_annotated.jpg"
                self._visualize_single_image(img_path, label_path, output_path, class_names)

        self.logger.info(f"Visualizations saved to {self.output_dir / 'visualizations'}")

    def _visualize_single_image(self, image_path: Path, annotation_path: Path,
                                 output_path: Path, class_names: Optional[List[str]]) -> bool:
        """Draw YOLO annotations on a single image.

        Args:
            image_path: Path to input image
            annotation_path: Path to YOLO annotation file
            output_path: Path to save annotated image
            class_names: List of class names

        Returns:
            True if successful, False otherwise
        """
        import cv2

        # Load image
        image = cv2.imread(str(image_path))
        if image is None:
            self.logger.warning(f"Failed to load image: {image_path}")
            return False

        height, width = image.shape[:2]

        # Read annotations
        if not annotation_path.exists() or annotation_path.stat().st_size == 0:
            # Save image as-is with "NO ANNOTATIONS" text
            cv2.putText(image, "NO ANNOTATIONS", (50, 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.imwrite(str(output_path), image)
            return True

        with open(annotation_path) as f:
            annotations = f.readlines()

        # Draw each annotation
        for annotation in annotations:
            parts = annotation.strip().split()
            if len(parts) != 5:
                continue

            class_id = int(parts[0])
            x_center_norm = float(parts[1])
            y_center_norm = float(parts[2])
            width_norm = float(parts[3])
            height_norm = float(parts[4])

            # Convert to pixel coordinates
            x_center = x_center_norm * width
            y_center = y_center_norm * height
            box_width = width_norm * width
            box_height = height_norm * height

            x_min = int(x_center - box_width / 2)
            y_min = int(y_center - box_height / 2)
            x_max = int(x_center + box_width / 2)
            y_max = int(y_center + box_height / 2)

            # Get color for class (deterministic based on class_id)
            np.random.seed(class_id * 12345)
            color = tuple(map(int, np.random.randint(0, 255, 3)))

            # Draw rectangle
            cv2.rectangle(image, (x_min, y_min), (x_max, y_max), color, 3)

            # Draw label
            class_name = class_names[class_id] if class_names and class_id < len(class_names) else f"Class {class_id}"
            label = f"{class_name}"

            # Draw label background
            (label_width, label_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
            cv2.rectangle(image, (x_min, y_min - label_height - 10),
                         (x_min + label_width, y_min), color, -1)

            # Draw label text
            cv2.putText(image, label, (x_min, y_min - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # Save visualization
        cv2.imwrite(str(output_path), image)
        return True

    def generate_preview(self, num_images: int = 5) -> None:
        """Generate a small preview dataset for testing.

        Args:
            num_images: Number of preview images to generate
        """
        import time
        start_time = time.time()

        self.logger.info(f"Generating {num_images} preview images")

        preview_dir = self.output_dir / "preview"
        preview_dir.mkdir(exist_ok=True)

        self.scene_manager.initialize()

        # Notify user of rendering device
        device_type = "GPU" if self.scene_manager.is_using_gpu() else "CPU"
        self.logger.info(f"=" * 60)
        self.logger.info(f"RENDERING MODE: {device_type}")
        self.logger.info(f"=" * 60)

        self.camera_orbit.setup_camera()

        # Enable output types (normals and depth can be called once)
        bproc.renderer.enable_normals_output()
        bproc.renderer.enable_depth_output(activate_antialiasing=False)
        # NOTE: Segmentation output must be enabled AFTER objects are loaded in each scene
        # See _generate_single_image() for segmentation setup

        for i in range(num_images):
            image_name = f"preview_{i:03d}"
            self._generate_single_image(image_name, preview_dir)

        elapsed_time = time.time() - start_time

        # Final memory log
        self._log_memory_usage(force=True)

        self.logger.info(f"Preview images saved to {preview_dir}")
        self.logger.info(f"Total time: {elapsed_time:.2f} seconds")
        self.logger.info(f"Peak memory usage: {self._peak_memory_mb/1024:.2f} GB ({self._peak_memory_mb:.0f} MB)")

        # Save preview summary to log directory if available
        if self.log_dir:
            self._save_preview_summary(num_images, elapsed_time)
            self._save_memory_log_csv()

    def _save_generation_summary(self, elapsed_time: float) -> None:
        """Save generation summary to log directory.

        Args:
            elapsed_time: Total time taken for generation
        """
        import json

        summary = {
            "total_images": self.config.num_images,
            "train_images": int(self.config.num_images * self.config.dataset.train_split),
            "val_images": int(self.config.num_images * self.config.dataset.val_split),
            "test_images": self.config.num_images - int(self.config.num_images * self.config.dataset.train_split) - int(self.config.num_images * self.config.dataset.val_split),
            "num_classes": self.model_loader.get_num_classes(),
            "class_names": self.model_loader.get_class_names(),
            "elapsed_time_seconds": elapsed_time,
            "elapsed_time_minutes": elapsed_time / 60,
            "avg_time_per_image": elapsed_time / self.config.num_images,
            "device_type": "GPU" if self.scene_manager.is_using_gpu() else "CPU",
            "output_directory": str(self.output_dir),
            "peak_memory_mb": self._peak_memory_mb,
            "peak_memory_gb": self._peak_memory_mb / 1024,
        }

        summary_path = self.log_dir / "generation_summary.json"
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)

        self.logger.info(f"Generation summary saved to {summary_path}")

    def _save_memory_log_csv(self) -> None:
        """Save detailed memory usage log to CSV file for analysis."""
        import csv

        if not self._memory_log_entries:
            self.logger.warning("No memory log entries to save")
            return

        csv_path = self.log_dir / "memory_usage.csv"

        with open(csv_path, 'w', newline='') as f:
            fieldnames = ['timestamp', 'images_generated', 'memory_mb', 'memory_gb',
                         'meshes', 'materials', 'textures', 'images']
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerows(self._memory_log_entries)

        self.logger.info(f"Memory usage log saved to {csv_path}")
        self.logger.info(f"Logged {len(self._memory_log_entries)} memory measurements")

    def _save_preview_summary(self, num_images: int, elapsed_time: float) -> None:
        """Save preview summary to log directory.

        Args:
            num_images: Number of preview images generated
            elapsed_time: Total time taken for preview generation
        """
        import json

        summary = {
            "preview_images": num_images,
            "num_classes": self.model_loader.get_num_classes(),
            "class_names": self.model_loader.get_class_names(),
            "elapsed_time_seconds": elapsed_time,
            "avg_time_per_image": elapsed_time / num_images if num_images > 0 else 0,
            "device_type": "GPU" if self.scene_manager.is_using_gpu() else "CPU",
            "output_directory": str(self.output_dir),
            "peak_memory_mb": self._peak_memory_mb,
            "peak_memory_gb": self._peak_memory_mb / 1024,
        }

        summary_path = self.log_dir / "preview_summary.json"
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)

        self.logger.info(f"Preview summary saved to {summary_path}")
