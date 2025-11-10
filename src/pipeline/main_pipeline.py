import cv2
import numpy as np
from typing import Dict, Any, Optional
from pathlib import Path

from src.detection.detector import IDCardDetector
from src.ocr.ocr_engine import OCREngine
from src.ocr.field_parser import FieldParser
from src.preprocessing.image_processing import ImageProcessor
from src.utils.logger import setup_logger

class IDCardPipeline:
    def __init__(self, config: Dict[str, Any]):
        self.logger = setup_logger(__name__)
        self.detector = IDCardDetector(
            model_path=config.get('detection.model', 'yolov8n.pt'),
            conf_threshold=config.get('detection.conf_threshold', 0.5)
        )
        self.ocr_engine = OCREngine(
            lang=config.get('ocr.lang', 'vi'),
            use_gpu=config.get('ocr.use_gpu', False)
        )
        self.image_processor = ImageProcessor()
        self.field_parser = FieldParser()
    
    def process(self, image_path: str) -> Dict[str, Any]:
        """
        Xử lý ảnh CCCD/Bằng lái từ đầu đến cuối
        """
        try:
            # Đọc ảnh
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Cannot read image: {image_path}")
            
            self.logger.info(f"Processing image: {image_path}")
            
            # Bước 1: Detect
            detections = self.detector.detect(image)
            if not detections:
                return {
                    'success': False,
                    'message': 'No ID card or driving license detected'
                }
            
            # Lấy detection có confidence cao nhất
            best_detection = max(detections, key=lambda x: x['confidence'])
            self.logger.info(f"Detected {best_detection['class_name']} with confidence {best_detection['confidence']:.2f}")
            
            # Bước 2: Crop ảnh
            cropped = self.detector.crop_detected_area(image, best_detection['bbox'])
            
            # Bước 3: Cải thiện ảnh
            enhanced = self.image_processor.enhance_image(cropped)
            
            # Bước 4: OCR
            ocr_results = self.ocr_engine.extract_text(cropped)
            full_text = '\n'.join([r['text'] for r in ocr_results])
            
            # Bước 5: Parse thông tin
            if 'cccd' in best_detection['class_name'].lower():
                parsed_data = self.field_parser.parse_cccd_front(full_text)
            elif 'driving' in best_detection['class_name'].lower():
                parsed_data = self.field_parser.parse_driving_license(full_text)
            else:
                parsed_data = {}
            
            return {
                'success': True,
                'detection': best_detection,
                'ocr_raw': ocr_results,
                'full_text': full_text,
                'parsed_data': parsed_data
            }
            
        except Exception as e:
            self.logger.error(f"Error processing image: {str(e)}")
            return {
                'success': False,
                'message': str(e)
            }