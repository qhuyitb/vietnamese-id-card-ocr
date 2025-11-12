from paddleocr import PaddleOCR
import numpy as np
import cv2
from typing import List, Dict, Any

class OCREngine:
    def __init__(self, lang: str = 'vi', use_gpu: bool = False):
        self.ocr = PaddleOCR(
            use_angle_cls=True,
            lang=lang,
            # det_db_thresh=0.3,      # ← Thêm: ngưỡng detection thấp hơn
            # det_db_box_thresh=0.5,   # ← Thêm: confidence box cao hơn
            # rec_batch_num=6,         # ← Thêm: batch size
            # use_space_char=True      # ← Quan trọng cho tiếng Việt
            # use_gpu=use_gpu,
            # show_log=False
        )
        print(f"✅ Khởi tạo OCR (lang={lang})")
    
    def extract_text(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Trích xuất text từ ảnh
        Returns: List of detected text with coordinates
        """
        try:
            if isinstance(image, str):
                image = cv2.imread(image)
            
            print(f"📐 Kích thước ảnh: {image.shape}")
            
            # Gọi OCR
            results = self.ocr.ocr(image)
            
            extracted_data = []
            
            print(f"🔍 Type of results: {type(results)}")
            
            if not results:
                print("⚠️  OCR trả về None")
                return extracted_data
            
            # Check structure
            print(f"🔍 Length of results: {len(results)}")
            print(f"🔍 Type of results[0]: {type(results[0])}")
            
            # Parse dựa trên type
            page_result = results[0]
            
            # Nếu là dict → Lấy key chứa text results
            if isinstance(page_result, dict):
                print(f"🔍 Dict keys: {list(page_result.keys())}")
                
                # Thử các key thường gặp
                if 'rec_texts' in page_result:
                    texts = page_result['rec_texts']
                    scores = page_result.get('rec_scores', [1.0] * len(texts))
                    polys = page_result.get('rec_polys', [[[0,0],[1,0],[1,1],[0,1]]] * len(texts))
                    
                    for text, score, poly in zip(texts, scores, polys):
                        if text and text.strip():
                            extracted_data.append({
                                'bbox': poly,
                                'text': text.strip(),
                                'confidence': float(score)
                            })
                            print(f"   ✓ '{text}' (conf: {score:.2f})")
                else:
                    print("⚠️  Không tìm thấy 'rec_texts' trong dict")
                    print(f"⚠️  Available keys: {list(page_result.keys())}")
                    
            # Nếu là list → Parse như bình thường
            elif isinstance(page_result, list):
                print(f"🔍 Số lượng lines: {len(page_result)}")
                
                if len(page_result) > 0:
                    print(f"🔍 Line đầu tiên: {page_result[0]}")
                
                for idx, line in enumerate(page_result):
                    try:
                        if not isinstance(line, (list, tuple)) or len(line) < 2:
                            continue
                        
                        bbox = line[0]
                        text_info = line[1]
                        
                        if isinstance(text_info, (list, tuple)) and len(text_info) >= 2:
                            text = str(text_info[0]).strip()
                            confidence = float(text_info[1])
                        else:
                            continue
                        
                        if text:
                            extracted_data.append({
                                'bbox': bbox,
                                'text': text,
                                'confidence': confidence
                            })
                            print(f"   ✓ [{idx}] '{text}' (conf: {confidence:.2f})")
                    
                    except Exception as e:
                        print(f"⚠️  Bỏ qua line {idx}: {e}")
                        continue
            else:
                print(f"⚠️  Unknown type: {type(page_result)}")
            
            print(f"✅ OCR phát hiện {len(extracted_data)} text blocks")
            return extracted_data
            
        except Exception as e:
            print(f"❌ Lỗi OCR: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_full_text(self, image: np.ndarray) -> str:
        """Lấy toàn bộ text từ ảnh"""
        results = self.extract_text(image)
        if not results:
            return ""
        return '\n'.join([r['text'] for r in results if r.get('text')])