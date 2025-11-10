from ultralytics import YOLO
import cv2
import numpy as np
from typing import List, Dict, Any
from pathlib import Path

class IDCardDetector:
    def __init__(self, model_path: str = "models/detection/yolov8n.pt", 
                 conf_threshold: float = 0.5):
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold
    
    def detect(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Phát hiện CCCD/Bằng lái trong ảnh
        Returns: List of detections with bbox coordinates
        """
        results = self.model(image, conf=self.conf_threshold)
        
        detections = []
        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                
                detections.append({
                    'bbox': [int(x1), int(y1), int(x2), int(y2)],
                    'confidence': conf,
                    'class': cls,
                    'class_name': self.model.names[cls]
                })
        
        return detections
    
    def crop_detected_area(self, image: np.ndarray, bbox: List[int]) -> np.ndarray:
        """Cắt vùng ảnh đã detect"""
        x1, y1, x2, y2 = bbox
        return image[y1:y2, x1:x2]
    
    def train(self, data_yaml: str, epochs: int = 100, imgsz: int = 640):
        """Train YOLO model"""
        results = self.model.train(
            data=data_yaml,
            epochs=epochs,
            imgsz=imgsz,
            patience=50,
            save=True,
            device='cpu'
        )
        return results