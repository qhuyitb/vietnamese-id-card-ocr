# src/pipeline/main_pipeline.py
import cv2
import numpy as np
from src.ocr.ocr_engine import OCREngine
from src.ocr.field_parser import FieldParser
from src.preprocessing.image_processing import ImageProcessor

def convert_numpy_to_native(obj):
    """Recursively convert numpy types to Python native types"""
    if isinstance(obj, dict):
        return {k: convert_numpy_to_native(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_numpy_to_native(item) for item in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.bool_):
        return bool(obj)
    else:
        return obj

class IDCardPipeline:
    def __init__(self):
        self.ocr_engine = OCREngine(lang='vi')
        self.field_parser = FieldParser()
    
    def process(self, image_input):
        """
        Xử lý ảnh CCCD/Bằng lái
        Args:
            image_input: numpy array hoặc đường dẫn file
        """
        try:
            # Đọc ảnh nếu là đường dẫn
            if isinstance(image_input, str):
                print(f"📂 Đọc ảnh từ: {image_input}")
                image = cv2.imread(image_input)
                if image is None:
                    raise ValueError(f"Không đọc được ảnh: {image_input}")
            elif isinstance(image_input, np.ndarray):
                image = image_input
            else:
                raise ValueError(f"image_input không hợp lệ: {type(image_input)}")
            
            print("⚠️  Skipping YOLOv8 detection (chưa train model)")
            print("🔍 OCR toàn bộ ảnh...")
            
            # OCR - Truyền numpy array
          
           
            # OCR - Truyền numpy array
            ocr_results = self.ocr_engine.extract_text(image)
            full_text = self.ocr_engine.get_full_text(image)
            
            if not ocr_results:
                return {
                    "success": False,
                    "message": "Không phát hiện text trong ảnh",
                    "full_text": "",
                    "ocr_results": [],
                    "parsed_data": {}
                }
            
            print(f"📄 Full text:\n{full_text}\n")
            
            # Parse thông tin
            parsed_data = self.field_parser.parse(full_text, ocr_results)
            
            # Build result và convert toàn bộ numpy types
            result = {
                "success": True,
                "detection": {
                    "bbox": [0, 0, int(image.shape[1]), int(image.shape[0])],
                    "confidence": 1.0,
                    "class_name": "full_image"
                },
                "full_text": full_text,
                "ocr_results": ocr_results,
                "parsed_data": parsed_data
            }
            
            # Convert tất cả numpy types sang Python native types
            return convert_numpy_to_native(result)
            
        except Exception as e:
            print(f"❌ Lỗi pipeline: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "message": str(e),
                "full_text": "",
                "ocr_results": [],
                "parsed_data": {}
            }