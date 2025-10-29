"""YOLO format annotation generation."""

from pathlib import Path
from typing import List, Tuple
import numpy as np
import cv2


class YOLOAnnotator:
    """Generates YOLO format annotations from rendered images."""

    def __init__(self, image_width: int, image_height: int):
        """Initialize YOLO annotator.

        Args:
            image_width: Width of rendered images
            image_height: Height of rendered images
        """
        self.image_width = image_width
        self.image_height = image_height

    def get_object_bbox_2d(
        self,
        obj: "bproc.types.MeshObject",
        camera_matrix: np.ndarray,
        world_to_camera: np.ndarray,
    ) -> Tuple[int, int, int, int]:
        """Get 2D bounding box of object in image space.

        Args:
            obj: Object to get bbox for
            camera_matrix: Camera intrinsic matrix
            world_to_camera: World to camera transformation matrix

        Returns:
            Tuple of (x_min, y_min, x_max, y_max) in pixel coordinates,
            or None if object not visible
        """
        # Get object bounding box in world coordinates
        bbox_3d = obj.get_bound_box()

        # Project 3D points to 2D
        points_2d = []
        for point_3d in bbox_3d:
            # Convert to homogeneous coordinates
            point_h = np.append(point_3d, 1)

            # Transform to camera space
            point_cam = world_to_camera @ point_h

            # Check if behind camera
            if point_cam[2] <= 0:
                continue

            # Project to image space
            point_img = camera_matrix @ point_cam[:3]
            point_img = point_img[:2] / point_img[2]

            points_2d.append(point_img)

        if not points_2d:
            return None

        points_2d = np.array(points_2d)

        # Get bounding rectangle
        x_min = int(np.min(points_2d[:, 0]))
        x_max = int(np.max(points_2d[:, 0]))
        y_min = int(np.min(points_2d[:, 1]))
        y_max = int(np.max(points_2d[:, 1]))

        # Clamp to image boundaries
        x_min = max(0, x_min)
        x_max = min(self.image_width - 1, x_max)
        y_min = max(0, y_min)
        y_max = min(self.image_height - 1, y_max)

        # Check if bbox is valid
        if x_max <= x_min or y_max <= y_min:
            return None

        return (x_min, y_min, x_max, y_max)

    def bbox_to_yolo_format(
        self, bbox: Tuple[int, int, int, int], class_id: int
    ) -> str:
        """Convert bounding box to YOLO format string.

        YOLO format: <class_id> <x_center> <y_center> <width> <height>
        All coordinates are normalized to [0, 1]

        Args:
            bbox: Bounding box as (x_min, y_min, x_max, y_max)
            class_id: Class ID

        Returns:
            YOLO format annotation string
        """
        x_min, y_min, x_max, y_max = bbox

        # Calculate center and dimensions
        width = x_max - x_min
        height = y_max - y_min
        x_center = x_min + width / 2
        y_center = y_min + height / 2

        # Normalize to [0, 1]
        x_center_norm = x_center / self.image_width
        y_center_norm = y_center / self.image_height
        width_norm = width / self.image_width
        height_norm = height / self.image_height

        return f"{class_id} {x_center_norm:.6f} {y_center_norm:.6f} {width_norm:.6f} {height_norm:.6f}"

    def generate_annotations_from_segmentation(
        self,
        segmentation_map: np.ndarray,
        instance_attribute_map: np.ndarray,
        objects: List,
    ) -> List[str]:
        """Generate YOLO annotations from segmentation maps.

        Args:
            segmentation_map: Segmentation map from BlenderProc
            instance_attribute_map: Instance attribute map
            objects: List of objects in scene

        Returns:
            List of YOLO format annotation strings
        """
        annotations = []

        for obj in objects:
            # Get class ID
            class_id = obj.get_cp("class_id")

            # Find object in segmentation map
            # This is a simplified version - you may need to adjust based on
            # how BlenderProc provides the segmentation data
            mask = segmentation_map == obj.get_cp("category_id", 0)

            if not mask.any():
                continue

            # Get bounding box from mask
            bbox = self._mask_to_bbox(mask)

            if bbox is None:
                continue

            # Convert to YOLO format
            yolo_annotation = self.bbox_to_yolo_format(bbox, class_id)
            annotations.append(yolo_annotation)

        return annotations

    def _mask_to_bbox(self, mask: np.ndarray) -> Tuple[int, int, int, int]:
        """Convert binary mask to bounding box.

        Args:
            mask: Binary mask

        Returns:
            Bounding box as (x_min, y_min, x_max, y_max)
        """
        # Find non-zero pixels
        coords = np.argwhere(mask)

        if coords.size == 0:
            return None

        # Get bounding box
        y_min, x_min = coords.min(axis=0)
        y_max, x_max = coords.max(axis=0)

        # Ensure valid bbox
        if x_max <= x_min or y_max <= y_min:
            return None

        return (int(x_min), int(y_min), int(x_max), int(y_max))

    def save_annotations(self, annotations: List[str], output_path: Path) -> None:
        """Save annotations to file in YOLO format.

        Args:
            annotations: List of YOLO format annotation strings
            output_path: Path to save annotations
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            f.write("\n".join(annotations))

    def visualize_annotations(
        self, image_path: Path, annotations: List[str], output_path: Path
    ) -> None:
        """Visualize annotations on image for debugging.

        Args:
            image_path: Path to image
            annotations: List of YOLO format annotations
            output_path: Path to save visualization
        """
        # Load image
        image = cv2.imread(str(image_path))

        # Draw each annotation
        for annotation in annotations:
            parts = annotation.split()
            class_id = int(parts[0])
            x_center = float(parts[1]) * self.image_width
            y_center = float(parts[2]) * self.image_height
            width = float(parts[3]) * self.image_width
            height = float(parts[4]) * self.image_height

            # Convert to corner coordinates
            x_min = int(x_center - width / 2)
            y_min = int(y_center - height / 2)
            x_max = int(x_center + width / 2)
            y_max = int(y_center + height / 2)

            # Draw rectangle
            color = self._get_class_color(class_id)
            cv2.rectangle(image, (x_min, y_min), (x_max, y_max), color, 2)

            # Draw class label
            cv2.putText(
                image,
                f"Class {class_id}",
                (x_min, y_min - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                2,
            )

        # Save visualization
        cv2.imwrite(str(output_path), image)

    def _get_class_color(self, class_id: int) -> Tuple[int, int, int]:
        """Get consistent color for class ID.

        Args:
            class_id: Class ID

        Returns:
            BGR color tuple
        """
        # Generate consistent color from class ID
        np.random.seed(class_id * 12345)
        color = tuple(map(int, np.random.randint(0, 255, 3)))
        return color
