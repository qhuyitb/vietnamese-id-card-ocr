# ID Card Detection System

Hệ thống phát hiện và trích xuất thông tin từ CCCD và Bằng lái xe Việt Nam.

## Tính năng

- ✅ Phát hiện CCCD/Bằng lái xe trong ảnh (YOLOv8)
- ✅ Trích xuất text từ ảnh (PaddleOCR)
- ✅ Parse thông tin cá nhân (Họ tên, Số CCCD, Ngày sinh...)
- ✅ REST API (FastAPI)
- ✅ Web Interface (React - tạo riêng)

## Cài đặt

### 1. Clone repository
```bash
git clone <https://github.com/qhuyitb/vietnamese-id-card-ocr>
cd id-card-detection
```

### 2. Tạo virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate  # Windows
```

### 3. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 4. Tải pretrained model
```bash
# YOLOv8 sẽ tự động tải khi chạy lần đầu
# Hoặc tải thủ công từ: https://github.com/ultralytics/assets/releases
```

## Sử dụng

### 1. Chuẩn bị dataset
```bash
python scripts/prepare_dataset.py
```

### 2. Train model (nếu có dataset)
📍 Trường hợp 1: TRAIN TRÊN GOOGLE COLAB
1. CHUẨN BỊ:
   ├─ Upload dataset lên Google Drive
   │  └─ MyDrive/CCCD_Dataset/
   │      ├─ train/
   │      ├─ valid/
   │      ├─ test/
   │      └─ data.yaml
   │
   └─ Chạy code Colab (đã cung cấp trước đó)

2. TRAINING TRÊN COLAB:
   ├─ Code tự động train
   ├─ Kết quả lưu vào Drive:
   │  └─ MyDrive/YOLO_Results/cccd_detection/
   │      └─ weights/
   │          ├─ best.pt      ← Model tốt nhất
   │          └─ last.pt      ← Model cuối cùng
   │
   └─ Thời gian: 30-60 phút (với GPU T4)

3. SAU KHI TRAIN XONG:
   ├─ Download từ Drive về máy local:
   │  └─ best.pt  (file này thôi là đủ)
   │
   └─ Copy vào project:
      └─ your_project/models/cccd_yolo/weights/best.pt

📍 Trường hợp 2: TRAIN TRÊN LOCAL (Nếu có GPU)
1. CHUẨN BỊ:
   └─ Dataset đã có sẵn trong project
      └─ your_project/CCCD_Dataset/
          ├─ train/
          ├─ valid/
          ├─ test/
          └─ data.yaml

2. KIỂM TRA GPU:
   └─ Chạy lệnh:
      python -c "import torch; print(torch.cuda.is_available())"
   
   ├─ True  → Có GPU, train được
   └─ False → Không GPU, SẼ RẤT CHẬM (không khuyên)

3. TRAINING LOCAL:
   └─ Chạy script:
      python scripts/train_detector.py
   
   ├─ Script tự động:
   │  ├─ Kiểm tra dataset
   │  ├─ Load pretrained model (yolov8s.pt)
   │  ├─ Train 100 epochs
   │  └─ Lưu kết quả
   │
   └─ Kết quả tự động lưu tại:
      └─ your_project/models/cccd_yolo/
          ├─ weights/
          │   ├─ best.pt   ← Dùng file này
          │   └─ last.pt
          ├─ results.png
          ├─ confusion_matrix.png
          └─ ...

4. SỬ DỤNG LUÔN:
   └─ Model đã ở đúng chỗ, chạy ngay:
      
```bash
python scripts/train_detector.py
```

### 3. Chạy API
```bash
python api/app.py
# hoặc
uvicorn api.app:app --reload
```

API sẽ chạy tại: http://localhost:8000

### 4. Test với ảnh
```bash
python main.py
```

## API Endpoints

### POST /api/process
Upload và xử lý ảnh CCCD/Bằng lái xe

**Request:**
- Content-Type: multipart/form-data
- Body: file (image)

**Response:**
```json
{
  "success": true,
  "detection": {
    "bbox": [100, 200, 500, 700],
    "confidence": 0.95,
    "class_name": "cccd_front"
  },
  "full_text": "...",
  "parsed_data": {
    "id_number": "001234567890",
    "full_name": "NGUYỄN VĂN A",
    "date_of_birth": "01/01/1990",
    ...
  }
}
```

## Cấu trúc thư mục

```
id-card-detection/
├── configs/          # File cấu hình
├── data/            # Dataset
├── models/          # Trained models
├── src/             # Source code
├── api/             # FastAPI application
├── scripts/         # Utility scripts
└── tests/           # Unit tests
```

## TODO

- [ ] Thu thập và label dataset
- [ ] Train custom YOLOv8 model
- [ ] Cải thiện OCR accuracy
- [ ] Thêm validation cho dữ liệu
- [ ] Xây dựng frontend React
- [ ] Deploy lên cloud

## License

MIT License
