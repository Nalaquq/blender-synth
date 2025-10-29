#!/usr/bin/env python3
"""
Test and visualize YOLO format annotations
Checks for missing annotations and visualizes bounding boxes
"""

import os
import sys
from pathlib import Path
import cv2
import numpy as np
from collections import defaultdict

def check_missing_annotations(output_dir):
    """Check for missing annotations across all splits"""
    print("=" * 60)
    print("CHECKING FOR MISSING ANNOTATIONS")
    print("=" * 60)

    splits = ['train', 'val', 'test']
    all_issues = []

    for split in splits:
        images_dir = Path(output_dir) / split / 'images'
        labels_dir = Path(output_dir) / split / 'labels'

        if not images_dir.exists() or not labels_dir.exists():
            print(f"\n[{split}] Directory not found, skipping...")
            continue

        # Get all image and label files
        image_files = {f.stem for f in images_dir.glob('*.jpg')}
        label_files = {f.stem for f in labels_dir.glob('*.txt')}

        # Find missing labels
        missing_labels = image_files - label_files
        # Find orphaned labels (labels without images)
        orphaned_labels = label_files - image_files

        print(f"\n[{split}] Statistics:")
        print(f"  Images: {len(image_files)}")
        print(f"  Labels: {len(label_files)}")

        if missing_labels:
            print(f"  ⚠ Missing labels: {len(missing_labels)}")
            for stem in sorted(missing_labels):
                print(f"    - {stem}")
                all_issues.append(f"{split}/{stem}: missing label file")

        if orphaned_labels:
            print(f"  ⚠ Orphaned labels: {len(orphaned_labels)}")
            for stem in sorted(orphaned_labels):
                print(f"    - {stem}")
                all_issues.append(f"{split}/{stem}: orphaned label file")

        # Check for empty label files
        empty_labels = []
        for label_file in labels_dir.glob('*.txt'):
            if label_file.stat().st_size == 0:
                empty_labels.append(label_file.stem)

        if empty_labels:
            print(f"  ⚠ Empty label files: {len(empty_labels)}")
            for stem in sorted(empty_labels):
                print(f"    - {stem}")
                all_issues.append(f"{split}/{stem}: empty label file")

        if not missing_labels and not orphaned_labels and not empty_labels:
            print(f"  ✓ All annotations present and non-empty")

    print("\n" + "=" * 60)
    if all_issues:
        print(f"SUMMARY: Found {len(all_issues)} issue(s)")
        return False
    else:
        print("SUMMARY: ✓ All annotations are present and valid!")
        return True

def visualize_annotations(output_dir, split='train', num_samples=5, save_dir=None):
    """Visualize annotations with bounding boxes"""
    print("\n" + "=" * 60)
    print(f"VISUALIZING ANNOTATIONS ({split} split)")
    print("=" * 60)

    images_dir = Path(output_dir) / split / 'images'
    labels_dir = Path(output_dir) / split / 'labels'

    if not images_dir.exists() or not labels_dir.exists():
        print(f"Error: {split} directories not found")
        return

    # Get all image files
    image_files = sorted(list(images_dir.glob('*.jpg')))[:num_samples]

    if not image_files:
        print("No images found!")
        return

    # Create save directory if needed
    if save_dir:
        save_path = Path(save_dir)
        save_path.mkdir(parents=True, exist_ok=True)

    # YOLO class names (adjust based on your dataset)
    class_names = {
        0: 'cable',
        1: 'connector',
        2: 'device'
    }

    # Colors for different classes (BGR format)
    colors = {
        0: (0, 255, 0),      # Green
        1: (255, 0, 0),      # Blue
        2: (0, 0, 255),      # Red
    }

    stats = defaultdict(int)

    for img_path in image_files:
        label_path = labels_dir / f"{img_path.stem}.txt"

        # Read image
        img = cv2.imread(str(img_path))
        if img is None:
            print(f"Failed to read image: {img_path}")
            continue

        h, w = img.shape[:2]

        # Read annotations
        num_objects = 0
        if label_path.exists():
            with open(label_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    parts = line.split()
                    if len(parts) < 5:
                        continue

                    class_id = int(parts[0])
                    x_center, y_center, width, height = map(float, parts[1:5])

                    # Convert YOLO format to pixel coordinates
                    x_center_px = int(x_center * w)
                    y_center_px = int(y_center * h)
                    box_w = int(width * w)
                    box_h = int(height * h)

                    x1 = int(x_center_px - box_w / 2)
                    y1 = int(y_center_px - box_h / 2)
                    x2 = int(x_center_px + box_w / 2)
                    y2 = int(y_center_px + box_h / 2)

                    # Draw bounding box
                    color = colors.get(class_id, (255, 255, 255))
                    cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)

                    # Draw label
                    label = class_names.get(class_id, f"class_{class_id}")
                    cv2.putText(img, label, (x1, y1 - 5),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                    num_objects += 1
                    stats[label] += 1

        # Add image filename to top
        cv2.putText(img, img_path.name, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(img, f"Objects: {num_objects}", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # Save or display
        if save_dir:
            output_path = save_path / f"viz_{img_path.name}"
            cv2.imwrite(str(output_path), img)
            print(f"✓ Saved visualization: {output_path}")
        else:
            # Display image
            cv2.imshow(f'Annotations - {img_path.name}', img)
            print(f"✓ Displaying {img_path.name} ({num_objects} objects)")
            print("  Press any key to continue, 'q' to quit...")
            key = cv2.waitKey(0)
            if key == ord('q'):
                cv2.destroyAllWindows()
                break

    cv2.destroyAllWindows()

    # Print statistics
    print("\n" + "=" * 60)
    print("ANNOTATION STATISTICS")
    print("=" * 60)
    print(f"Images processed: {len(image_files)}")
    if stats:
        print("Objects by class:")
        for class_name, count in sorted(stats.items()):
            print(f"  {class_name}: {count}")
    else:
        print("No annotations found!")

if __name__ == '__main__':
    output_dir = '/home/nalkuq/blender-synth/output'

    # Check for missing annotations
    annotations_valid = check_missing_annotations(output_dir)

    # Visualize annotations
    print("\nStarting visualization...")
    print("Note: Visualizations will be saved to 'output/visualizations'")

    visualize_annotations(
        output_dir,
        split='train',
        num_samples=9,  # Visualize all 9 images
        save_dir='/home/nalkuq/blender-synth/output/visualizations'
    )

    print("\n" + "=" * 60)
    print("TESTING COMPLETE")
    print("=" * 60)
    if annotations_valid:
        print("✓ All checks passed!")
        sys.exit(0)
    else:
        print("⚠ Some issues found (see above)")
        sys.exit(1)
