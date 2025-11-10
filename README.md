"""
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
git clone <your-repo>
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
"""