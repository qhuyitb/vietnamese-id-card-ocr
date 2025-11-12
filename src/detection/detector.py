"""
CCCD Detector - Phát hiện và crop các vùng thông tin trên CCCD
"""
import sys
from pathlib import Path

# Thêm thư mục gốc vào sys.path
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(ROOT))

from ultralytics import YOLO
import cv2
import numpy as np
from typing import List, Dict, Any, Optional

class CCCDDetector:
    """Detector cho CCCD Việt Nam"""
    
    # 12 classes theo dataset
    CLASS_NAMES = [
        'current_place',  # 0: Nơi thường trú
        'dob',            # 1: Ngày sinh
        'expire_date',    # 2: Ngày hết hạn
        'features',       # 3: Đặc điểm nhận dạng (mặt sau)
        'finger_print',   # 4: Vân tay (mặt sau)
        'gender',         # 5: Giới tính
        'id',             # 6: Số CCCD
        'issue_date',     # 7: Ngày cấp (mặt sau)
        'name',           # 8: Họ tên
        'nationality',    # 9: Quốc tịch
        'origin_place',   # 10: Quê quán
        'qr'              # 11: Mã QR
    ]
    
    def __init__(self, model_path: Optional[str] = None, conf_threshold: float = 0.5):
        """
        Initialize CCCD Detector
        
        Args:
            model_path: Đường dẫn đến model (None = dùng model mặc định)
            conf_threshold: Ngưỡng confidence (0-1)
        """
        # Nếu không có model_path, dùng model trong thư mục models/
        if model_path is None:
            model_path = str(ROOT / 'models' / 'cccd_yolo' / 'weights' / 'best.pt')
        
        self.model_path = Path(model_path)
        
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"❌ Model không tồn tại: {model_path}\n"
                f"   Vui lòng train model trước bằng: python scripts/train_detector.py"
            )
        
        print(f"📦 Loading model: {model_path}")
        self.model = YOLO(str(model_path))
        self.conf_threshold = conf_threshold
        print(f"✓ Model loaded!")
        print(f"✓ Classes: {len(self.CLASS_NAMES)} classes")
    
    def detect(self, image: np.ndarray, conf: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Phát hiện các vùng thông tin trên CCCD
        
        Args:
            image: Ảnh đầu vào (numpy array BGR)
            conf: Confidence threshold (override default)
            
        Returns:
            List of detections
        """
        conf = conf or self.conf_threshold
        results = self.model(image, conf=conf, verbose=False)
        
        detections = []
        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                class_name = self.model.names[class_id]
                
                detections.append({
                    'bbox': [int(x1), int(y1), int(x2), int(y2)],
                    'confidence': confidence,
                    'class_id': class_id,
                    'class_name': class_name
                })
        
        # Sort theo class_id để dễ đọc
        detections.sort(key=lambda x: x['class_id'])
        
        return detections
    
    def detect_and_crop(self, image: np.ndarray, conf: Optional[float] = None) -> Dict[str, np.ndarray]:
        """
        Detect và crop các vùng thông tin
        
        Returns:
            Dictionary: {class_name: cropped_image}
        """
        detections = self.detect(image, conf)
        
        cropped_regions = {}
        for det in detections:
            class_name = det['class_name']
            bbox = det['bbox']
            cropped = self.crop_bbox(image, bbox)
            
            # Nếu có nhiều vùng cùng class, thêm số thứ tự
            if class_name in cropped_regions:
                i = 2
                while f"{class_name}_{i}" in cropped_regions:
                    i += 1
                class_name = f"{class_name}_{i}"
            
            cropped_regions[class_name] = cropped
        
        return cropped_regions
    
    def crop_bbox(self, image: np.ndarray, bbox: List[int]) -> np.ndarray:
        """Cắt vùng ảnh theo bbox"""
        x1, y1, x2, y2 = bbox
        # Đảm bảo bbox nằm trong ảnh
        h, w = image.shape[:2]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)
        return image[y1:y2, x1:x2]
    
    def visualize(self, image: np.ndarray, conf: Optional[float] = None, 
                  save_path: Optional[str] = None) -> np.ndarray:
        """
        Vẽ bounding boxes lên ảnh
        """
        detections = self.detect(image, conf)
        result_img = image.copy()
        
        # Màu cho mỗi class
        colors = [
            (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
            (255, 0, 255), (0, 255, 255), (128, 0, 0), (0, 128, 0),
            (0, 0, 128), (128, 128, 0), (128, 0, 128), (0, 128, 128)
        ]
        
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            class_name = det['class_name']
            class_id = det['class_id']
            confidence = det['confidence']
            
            # Chọn màu theo class_id
            color = colors[class_id % len(colors)]
            
            # Vẽ bbox
            cv2.rectangle(result_img, (x1, y1), (x2, y2), color, 2)
            
            # Vẽ label với background
            label = f"{class_name}: {confidence:.2f}"
            (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(result_img, (x1, y1 - label_h - 10), (x1 + label_w, y1), color, -1)
            cv2.putText(result_img, label, (x1, y1 - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        if save_path:
            cv2.imwrite(save_path, result_img)
            print(f"✓ Saved: {save_path}")
        
        return result_img
    
    def process_image(self, image_path: str, output_dir: Optional[str] = None, 
                     conf: Optional[float] = None) -> Dict[str, Any]:
        """
        Xử lý một ảnh CCCD hoàn chỉnh
        
        Args:
            image_path: Đường dẫn ảnh CCCD
            output_dir: Thư mục lưu kết quả (optional)
            conf: Confidence threshold
            
        Returns:
            Dictionary chứa detections và cropped regions
        """
        # Đọc ảnh
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"❌ Không thể đọc ảnh: {image_path}")
        
        print(f"📸 Processing: {image_path}")
        
        # Detect
        detections = self.detect(image, conf)
        print(f"✓ Detected {len(detections)} regions:")
        for det in detections:
            print(f"   - {det['class_name']}: {det['confidence']:.2f}")
        
        # Crop regions
        cropped_regions = self.detect_and_crop(image, conf)
        
        # Visualize
        vis_image = self.visualize(image, conf)
        
        # Lưu kết quả
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Lưu visualization
            img_name = Path(image_path).stem
            vis_path = output_path / f"{img_name}_detected.jpg"
            cv2.imwrite(str(vis_path), vis_image)
            print(f"✓ Saved visualization: {vis_path}")
            
            # Lưu cropped regions
            for class_name, cropped in cropped_regions.items():
                crop_path = output_path / f"{img_name}_{class_name}.jpg"
                cv2.imwrite(str(crop_path), cropped)
            
            print(f"✓ Saved {len(cropped_regions)} cropped regions")
        
        return {
            'detections': detections,
            'cropped_regions': cropped_regions,
            'visualization': vis_image
        }


# DEMO USAGE
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='CCCD Detection Demo')
    parser.add_argument('--image', type=str, required=True, help='Đường dẫn ảnh CCCD')
    parser.add_argument('--model', type=str, default=None, help='Đường dẫn model (optional)')
    parser.add_argument('--output', type=str, default='output/detections', help='Thư mục output')
    parser.add_argument('--conf', type=float, default=0.5, help='Confidence threshold')
    
    args = parser.parse_args()
    
    try:
        # Khởi tạo detector
        detector = CCCDDetector(model_path=args.model, conf_threshold=args.conf)
        
        # Process image
        results = detector.process_image(
            image_path=args.image,
            output_dir=args.output,
            conf=args.conf
        )
        
        print(f"\n✅ Done! Kết quả đã lưu tại: {args.output}")
        
    except FileNotFoundError as e:
        print(f"\n❌ Lỗi: {e}")
        print("\nĐể train model, chạy: python scripts/train_detector.py")
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()