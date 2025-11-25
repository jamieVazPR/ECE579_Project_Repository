"""
JSON to YOLO Format Converter
Converts CholecT50 surgical action annotations to YOLO format
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class JSONToYOLOConverter:
    """
    Converts surgical action triplet annotations from JSON to YOLO format.
    
    YOLO format: <class_id> <x_center> <y_center> <width> <height>
    All coordinates are normalized (0-1)
    """
    
    def __init__(self, image_width: int = 1920, image_height: int = 1080):
        """
        Initialize converter with image dimensions.
        
        Args:
            image_width: Width of images in pixels
            image_height: Height of images in pixels
        """
        self.image_width = image_width
        self.image_height = image_height
        self.categories = {}
        
    def load_json(self, json_path: str) -> Dict:
        """Load JSON annotation file."""
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            logger.info(f"Loaded JSON: {json_path}")
            return data
        except Exception as e:
            logger.error(f"Error loading {json_path}: {e}")
            raise
    
    def bbox_to_yolo(self, bbox: List[float]) -> Tuple[float, float, float, float]:
        """
        Convert bounding box from [x1, y1, width, height] to YOLO format.
        
        Args:
            bbox: [x1, y1, box_width, box_height]
            
        Returns:
            (x_center, y_center, width, height) normalized to [0, 1]
        """
        x1, y1, bw, bh = bbox
        
        # Calculate center coordinates
        x_center = (x1 + bw / 2) / self.image_width
        y_center = (y1 + bh / 2) / self.image_height
        
        # Normalize width and height
        width = bw / self.image_width
        height = bh / self.image_height
        
        # Clip values to [0, 1]
        x_center = max(0, min(1, x_center))
        y_center = max(0, min(1, y_center))
        width = max(0, min(1, width))
        height = max(0, min(1, height))
        
        return x_center, y_center, width, height
    
    def extract_categories(self, json_data: Dict) -> Dict:
        """Extract category mappings from JSON data."""
        categories = json_data.get('categories', {})
        self.categories = categories
        return categories
    
    def convert_frame_annotations(self, frame_annotations: List[List[int]]) -> List[str]:
  
        for ann in frame_annotations:
            if len(ann) >= 1:
                return [str(int(ann[0]))]  # instrument id as class
        return []  # no label for this frame


    
    def convert_json_to_yolo(self, json_path: str, output_dir: str, 
                         use_triplet_class: bool = False) -> None:

    # Load and prep
        json_data = self.load_json(json_path)
        self.extract_categories(json_data)

        annotations = json_data.get('annotations', {})
        if not isinstance(annotations, dict):
            logger.warning(f"{json_path}: 'annotations' is not a dict; skipping.")
            return

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Prefix: prefer JSON's "video", else fall back to file stem
        video_id = json_data.get('video', Path(json_path).stem)

        # numeric-first sorting for frame keys
        def _sort_key(k: str):
            try:
                return (0, int(k))
            except Exception:
                return (1, k)

        converted_count = 0
        skipped_empty = 0

        for frame_id in sorted(annotations.keys(), key=_sort_key):
            frame_annotations = annotations[frame_id]

            # Build the single-label (classification) line
            yolo_lines = self.convert_frame_annotations(frame_annotations)
            if not yolo_lines:
                skipped_empty += 1
                continue

            # File name: VID##_{frame:06d}.txt, e.g., VID01_000048.txt
            try:
                fid = int(frame_id)
                out_name = f"VID_{video_id}_{fid:06d}.txt"
            except Exception:
                out_name = f"VID_{video_id}_{frame_id}.txt"

            output_file = output_path / out_name
            with open(output_file, "w", encoding="utf-8") as f:
                # classification: exactly one integer per file
                f.write(yolo_lines[0].strip() + "\n")

            converted_count += 1

        logger.info(f"{video_id}: converted {converted_count} frames; skipped {skipped_empty} empty.")
        logger.info(f"Output saved to: {output_dir}")

    
    def batch_convert(self, json_files: List[str], output_base_dir: str) -> None:
        """
        Convert multiple JSON files to YOLO format.
        
        Args:
            json_files: List of JSON file paths
            output_base_dir: Base directory for outputs
        """
        for json_file in json_files:
            json_path = Path(json_file)
            video_name = json_path.stem
            output_dir = os.path.join(output_base_dir, video_name)
            
            logger.info(f"Converting {json_file}...")
            try:
                self.convert_json_to_yolo(json_file, output_dir)
            except Exception as e:
                logger.error(f"Error converting {json_file}: {e}")
    
    def create_class_mapping_file(self, output_path: str, 
                                   category_type: str = 'instrument') -> None:
        """
        Create a class mapping file for YOLO training.
        
        Args:
            output_path: Path to save the mapping file
            category_type: Type of category ('instrument', 'triplet', etc.)
        """
        if not self.categories:
            logger.warning("No categories loaded. Load JSON data first.")
            return
        
        categories = self.categories.get(category_type, {})
        
        with open(output_path, 'w') as f:
            for class_id, class_name in sorted(categories.items(), 
                                              key=lambda x: int(x[0])):
                f.write(f"{class_id}: {class_name}\n")
        
        logger.info(f"Class mapping saved to: {output_path}")
    
    def create_yaml_config(self, output_path: str, train_path: str, 
                          val_path: str, category_type: str = 'instrument') -> None:
        """
        Create YOLO dataset configuration YAML file.
        
        Args:
            output_path: Path to save YAML file
            train_path: Path to training images
            val_path: Path to validation images
            category_type: Type of category to use
        """
        if not self.categories:
            logger.warning("No categories loaded. Load JSON data first.")
            return
        
        categories = self.categories.get(category_type, {})
        names = [categories[str(i)] for i in range(len(categories))]
        
        yaml_content = f"""# Dataset configuration for YOLO
        train: {train_path}
        val: {val_path}

        # Number of classes
        nc: {len(categories)}

        # Class names
        names: {names}
        """
        
        with open(output_path, 'w') as f:
            f.write(yaml_content)
        
        logger.info(f"YAML config saved to: {output_path}")


def main():
    """Batch convert all JSON files in a folder."""
    input_dir = "labels"        # <--- folder containing VID*.json
    output_base = "yolo_annotations"      # <--- folder to create outputs

    converter = JSONToYOLOConverter(image_width=1920, image_height=1080)

    # gather all json files in folder
    json_files = [str(p) for p in Path(input_dir).glob("*.json")]

    if not json_files:
        print("No json files found in", input_dir)
        return

    converter.batch_convert(json_files, output_base)

    print("\nALL DONE!")
    print("Converted", len(json_files), "files.")
    print("Output saved under:", output_base)



if __name__ == "__main__":
    main()