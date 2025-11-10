from paddleocr import PaddleOCR
import numpy as np
from typing import List, Dict, Tuple
import re

class OCREngine:
    def __init__(self, lang: str = 'vi', use_gpu: bool = False):
        self.ocr = PaddleOCR(
            use_angle_cls=True,
            lang=lang,
            use_gpu=use_gpu,
            show_log=False
        )
    
    def extract_text(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Trích xuất text từ ảnh
        Returns: List of detected text with coordinates
        """
        results = self.ocr.ocr(image, cls=True)
        
        extracted_data = []
        if results and results[0]:
            for line in results[0]:
                bbox = line[0]
                text = line[1][0]
                confidence = line[1][1]
                
                extracted_data.append({
                    'bbox': bbox,
                    'text': text,
                    'confidence': confidence
                })
        
        return extracted_data
    
    def get_full_text(self, image: np.ndarray) -> str:
        """Lấy toàn bộ text từ ảnh"""
        results = self.extract_text(image)
        return '\n'.join([r['text'] for r in results])