"""
Script để chuẩn bị dataset cho training
"""
import os
import shutil
from pathlib import Path
import yaml

def prepare_yolo_dataset(raw_data_dir: str, output_dir: str, split_ratio=(0.7, 0.2, 0.1)):
    """
    Chuẩn bị dataset theo format YOLO
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Tạo thư mục
    for split in ['train', 'val', 'test']:
        (output_path / split / 'images').mkdir(parents=True, exist_ok=True)
        (output_path / split / 'labels').mkdir(parents=True, exist_ok=True)
    
    # Tạo data.yaml
    data_yaml = {
        'path': str(output_path.absolute()),
        'train': 'train/images',
        'val': 'val/images',
        'test': 'test/images',
        'nc': 4,  # number of classes
        'names': ['cccd_front', 'cccd_back', 'driving_license_front', 'driving_license_back']
    }
    
    with open(output_path / 'data.yaml', 'w') as f:
        yaml.dump(data_yaml, f)
    
    print(f"Dataset prepared at: {output_path}")
    print("Please add your images and labels to the train/val/test folders")

if __name__ == "__main__":
    prepare_yolo_dataset("data/raw", "data/processed")
