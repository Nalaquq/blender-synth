"""Visualize YOLO annotations on images."""

import cv2
import numpy as np
from pathlib import Path
import sys

def visualize_yolo_annotations(image_path, annotation_path, output_path, class_names=None):
    """Draw YOLO annotations on image."""
    # Load image
    image = cv2.imread(str(image_path))
    if image is None:
        print(f"Failed to load image: {image_path}")
        return False
    
    height, width = image.shape[:2]
    
    # Read annotations
    if not annotation_path.exists() or annotation_path.stat().st_size == 0:
        print(f"No annotations found for {image_path.name}")
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
        
        # Get color for class
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
    print(f"✓ Visualized {len(annotations)} annotations: {output_path.name}")
    return True

if __name__ == "__main__":
    # Load class names
    classes_file = Path("output/classes.txt")
    if classes_file.exists():
        with open(classes_file) as f:
            class_names = [line.strip() for line in f]
    else:
        class_names = None

    # Visualize train images
    output_dir = Path("output/visualizations")
    output_dir.mkdir(exist_ok=True)

    train_images = sorted(Path("output/train/images").glob("*.jpg"))
    train_labels = Path("output/train/labels")

    print(f"Visualizing {len(train_images)} training images...")
    for img_path in train_images:
        label_path = train_labels / f"{img_path.stem}.txt"
        output_path = output_dir / f"{img_path.stem}_annotated.jpg"
        visualize_yolo_annotations(img_path, label_path, output_path, class_names)

    print(f"\nVisualizations saved to: {output_dir}")
