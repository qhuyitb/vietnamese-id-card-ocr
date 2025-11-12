# 🇻🇳 Vietnamese ID Card & Driving License OCR System

**Hệ thống phát hiện (Detection) và trích xuất (OCR) thông tin tự động từ Thẻ Căn cước Công dân (CCCD) và Bằng lái xe Việt Nam.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Framework: FastAPI](https://img.shields.io/badge/API-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)

---

## ✨ Tính năng chính (Features)

| Trạng thái | Tính năng | Công nghệ sử dụng | Mô tả |
| :---: | :--- | :--- | :--- |
| ✅ | **Object Detection** | **YOLOv8** | Phát hiện vị trí của CCCD/Bằng lái xe và các trường thông tin trên ảnh. |
| ✅ | **Text Extraction (OCR)** | **PaddleOCR** | Trích xuất văn bản chính xác từ các vùng đã được phát hiện. |
| ✅ | **Data Parsing & Structuring** | Custom Script | Chuẩn hóa thông tin cá nhân (Họ tên, Số CCCD, Ngày sinh, v.v.) thành cấu trúc JSON. |
| ✅ | **REST API** | **FastAPI** | Cung cấp giao diện lập trình ứng dụng dễ dàng tích hợp. |
| ⬜ | **Web Interface** | React (Tùy chọn) | Giao diện người dùng web để upload và xem kết quả. (Sẽ phát triển riêng) |

---

## 🛠️ Cài đặt (Setup)

### 1. Clone Repository

```bash
git clone https://github.com/qhuyitb/vietnamese-id-card-ocr
cd vietnamese-id-card-ocr
```

### 2. Tạo Virtual Environment

```bash
python -m venv venv

# Kích hoạt môi trường (Linux/Mac)
source venv/bin/activate

# Kích hoạt môi trường (Windows)
venv\Scripts\activate
```

### 3. Cài đặt Dependencies

```bash
pip install -r requirements.txt
```

### 4. Chuẩn bị Dataset

Dataset được tổ chức theo cấu trúc:

```
CCCD_Dataset/
├── train/
│   ├── images/
│   └── labels/
├── valid/
│   ├── images/
│   └── labels/
├── test/
│   ├── images/
│   └── labels/
└── data.yaml
```

**File `data.yaml`** (tạo file này nếu chưa có):

```yaml
train: train/images
val: valid/images
test: test/images

nc: 12
names: ['current_place', 'dob', 'expire_date', 'features', 'finger_print', 
        'gender', 'id', 'issue_date', 'name', 'nationality', 'origin_place', 'qr']
```

---

## 🚀 Sử dụng (Usage)

### 1. Huấn luyện Mô hình Detector

Có 2 phương án: **Google Colab** (khuyên dùng) hoặc **Local** (yêu cầu GPU).

#### 📍 PHƯƠNG ÁN A: Train trên Google Colab ⭐ (Khuyên dùng)

**Bước 1: Upload dataset lên Google Drive**
- Tạo thư mục `MyDrive/CCCD_Dataset/`
- Upload toàn bộ thư mục `train/`, `valid/`, `test/` và file `data.yaml`

**Bước 2: Chạy code Colab**
- Mở Google Colab: https://colab.research.google.com/
- Tạo notebook mới
- Chọn Runtime → Change runtime type → **T4 GPU**
- Copy và chạy code sau:

```python
# ===== KIỂM TRA GPU =====
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None'}")

# ===== CÀI ĐẶT =====
!pip install ultralytics -q

# ===== KẾT NỐI DRIVE =====
from google.colab import drive
drive.mount('/content/drive')

# ===== THIẾT LẬP ĐƯỜNG DẪN =====
DATASET_PATH = '/content/drive/MyDrive/CCCD_Dataset'

# ===== TRAIN =====
from ultralytics import YOLO

model = YOLO('yolov8s.pt')

results = model.train(
    data=f'{DATASET_PATH}/data.yaml',
    epochs=100,
    imgsz=640,
    batch=16,
    name='cccd_detection',
    project='/content/drive/MyDrive/YOLO_Results',
    exist_ok=True,
    patience=50,
    save=True,
    save_period=10,
    device=0,
    workers=2,
)

print(f"✅ Training completed!")
print(f"Best model: {results.save_dir}/weights/best.pt")
```

**Bước 3: Download model**
- Sau khi train xong (30-60 phút), vào Drive
- Download file: `YOLO_Results/cccd_detection/weights/best.pt`

**Bước 4: Copy model vào project**

```bash
# Chạy script tự động
python scripts/setup_model_from_colab.py

# Hoặc copy thủ công vào:
# models/cccd_yolo/weights/best.pt
```

---

#### 📍 PHƯƠNG ÁN B: Train trên Local (Yêu cầu GPU)

**Bước 1: Kiểm tra GPU**

```bash
python -c "import torch; print(torch.cuda.is_available())"
# True: Có GPU, có thể train
# False: Không có GPU, SẼ RẤT CHẬM (không khuyên)
```

**Bước 2: Train**

```bash
python scripts/train_detector.py
```

Script sẽ:
- ✅ Tự động kiểm tra dataset
- ✅ Load pretrained model `yolov8s.pt`
- ✅ Train 100 epochs
- ✅ Lưu model tại: `models/cccd_yolo/weights/best.pt`

Thời gian: 30-90 phút (tùy GPU)

---

### 2. Test Detection

Sau khi có model, test trên ảnh:

```bash
# Test 1 ảnh
python src/detection/detector.py --image test_images/sample.jpg --output output/detections

# Với confidence threshold tùy chỉnh
python src/detection/detector.py --image test_images/sample.jpg --conf 0.6 --output output/detections
```

Kết quả được lưu trong thư mục `output/detections/`:
- `sample_detected.jpg`: Ảnh với bounding boxes
- `sample_id.jpg`, `sample_name.jpg`, ...: Các vùng đã crop

---

### 3. Chạy REST API

```bash
# Khởi chạy API
python api/app.py

# Hoặc dùng uvicorn (tự động reload khi code thay đổi)
uvicorn api.app:app --reload --host 0.0.0.0 --port 8000
```

API sẽ chạy tại: **http://localhost:8000**

Xem API docs: **http://localhost:8000/docs**

---

### 4. Test toàn bộ hệ thống

```bash
python main.py
```

---

## 🌐 API Endpoints

### **POST** `/api/process`

Upload ảnh CCCD/Bằng lái xe và trích xuất thông tin.

#### Request

| Thuộc tính | Kiểu dữ liệu | Mô tả |
|------------|--------------|-------|
| `Content-Type` | `multipart/form-data` | Bắt buộc |
| `file` | Image (JPEG, PNG) | Ảnh cần xử lý |

#### Response (JSON)

```json
{
  "success": true,
  "detection": {
    "bbox": [100, 200, 500, 700],
    "confidence": 0.95,
    "class_name": "cccd_front"
  },
  "regions": {
    "id": "070095002564",
    "name": "TRẦN THẾ HOÀNG",
    "dob": "24/01/1995",
    "gender": "Nam",
    "nationality": "Việt Nam",
    "origin_place": "Bình Định, Kiên Xương, Thái Bình",
    "current_place": "Tổ 5 Thạnh Trịnh, Thạnh Lương, Thị xã Bình Long, Bình Phước",
    "expire_date": "24/01/2035"
  }
}
```

#### Test với cURL

```bash
curl -X POST "http://localhost:8000/api/process" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test_images/cccd.jpg"
```

---

## 📁 Cấu trúc thư mục (Project Structure)

```
vietnamese-id-card-ocr/
├── api/                          # FastAPI application
│   ├── app.py                    # Main API file
│   └── routes/                   # API endpoints
├── configs/                      # File cấu hình
├── models/                       # Models đã train
│   └── cccd_yolo/
│       └── weights/
│           └── best.pt          # YOLO model (sau khi train)
├── scripts/                      # Utility scripts
│   ├── train_detector.py        # Train YOLOv8 (local)
│   └── setup_model_from_colab.py # Setup model từ Colab
├── src/                          # Source code
│   ├── detection/
│   │   └── detector.py          # CCCD Detector
│   ├── ocr/                     # PaddleOCR wrapper
│   ├── preprocessing/           # Image preprocessing
│   ├── utils/                   # Utilities
│   └── pipeline/                # Full processing pipeline
├── tests/                        # Unit tests
├── test_images/                  # Test images
├── output/                       # Output results
├── CCCD_Dataset/                 # Training dataset
│   ├── train/
│   ├── valid/
│   ├── test/
│   └── data.yaml
├── main.py                       # Quick test script
├── requirements.txt              # Dependencies
└── README.md                     # This file
```

---

## 🔧 Cấu hình (Configuration)

Các tham số có thể điều chỉnh trong `scripts/train_detector.py`:

```python
EPOCHS = 100        # Số epochs (100-200)
IMG_SIZE = 640      # Kích thước ảnh
MODEL_SIZE = 's'    # 'n', 's', 'm', 'l', 'x'
```

---

## 📊 Kết quả (Results)

Sau khi train, các file kết quả trong `models/cccd_yolo/`:

```
models/cccd_yolo/
├── weights/
│   ├── best.pt              # Model tốt nhất
│   └── last.pt              # Model cuối cùng
├── results.png              # Biểu đồ loss/metrics
├── confusion_matrix.png     # Ma trận nhầm lẫn
├── F1_curve.png            # F1 score curve
├── P_curve.png             # Precision curve
└── R_curve.png             # Recall curve
```

---

## 🐛 Xử lý lỗi (Troubleshooting)

### Lỗi: "Model không tồn tại"

```bash
# Kiểm tra model đã có chưa
ls models/cccd_yolo/weights/best.pt

# Nếu chưa có, train lại hoặc copy từ Colab
python scripts/train_detector.py
```

### Lỗi: "CUDA out of memory"

```python
# Giảm batch size trong train_detector.py
batch=8  # thay vì 16
```

### Lỗi: "No module named 'ultralytics'"

```bash
pip install ultralytics
```

---

## 💡 TODO (Kế hoạch Phát triển)

- [ ] Thu thập và gán nhãn dataset cho Bằng lái xe
- [ ] Tích hợp PaddleOCR để đọc text từ các vùng đã detect
- [ ] Cải thiện độ chính xác OCR trên ảnh mờ/nghiêng
- [ ] Xây dựng Frontend React
- [ ] Validation dữ liệu (kiểm tra format số CCCD, ngày sinh, v.v.)
- [ ] Deploy lên cloud (AWS/GCP/Azure)
- [ ] Hỗ trợ batch processing (xử lý nhiều ảnh cùng lúc)
- [ ] Thêm logging và monitoring

---

## 🤝 Đóng góp (Contributing)

Mọi đóng góp đều được chào đón! Vui lòng:

1. Fork repository
2. Tạo branch mới (`git checkout -b feature/AmazingFeature`)
3. Commit thay đổi (`git commit -m 'Add some AmazingFeature'`)
4. Push lên branch (`git push origin feature/AmazingFeature`)
5. Mở Pull Request

---

## 📜 Giấy phép (License)

Dự án này được phát hành dưới giấy phép **MIT License**. Xem file [LICENSE](LICENSE) để biết chi tiết.

---

## ⚠️ Lưu ý sử dụng & Từ chối trách nhiệm

Dự án này được phát triển **vì mục đích học tập, nghiên cứu và minh họa kỹ thuật**. Không được sử dụng phần mềm này cho bất kỳ hành vi bất hợp pháp nào, xâm phạm quyền riêng tư, hoặc thu thập/chia sẻ dữ liệu cá nhân mà không có sự đồng ý hợp pháp của chủ sở hữu dữ liệu.

**Tác giả và các đóng góp viên không chịu trách nhiệm** cho bất kỳ tổn thất, thiệt hại, hậu quả pháp lý hoặc trách nhiệm phát sinh từ việc sử dụng, lạm dụng hoặc triển khai phần mềm này. Phần mềm được cung cấp **“AS IS”** (nguyên trạng) — không có bất kỳ bảo đảm nào về tính chính xác, an toàn, khả năng tương thích hay tính phù hợp cho mục đích cụ thể.

---

## 📧 Liên hệ (Contact)

- **GitHub**: [@qhuyitb](https://github.com/qhuyitb)
- **Email**: toquanghuy1719@gmail.com

---

## 🙏 Ghi nhận (Acknowledgments)

- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics) - Object Detection
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - Text Recognition
- [FastAPI](https://fastapi.tiangolo.com/) - API Framework