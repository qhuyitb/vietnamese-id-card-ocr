"""
Script để train YOLOv8 model - CCCD Detection
"""
import sys
from pathlib import Path

# Thêm thư mục gốc vào sys.path
ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from ultralytics import YOLO
import torch

def train_yolo(data_yaml: str, epochs: int = 100, imgsz: int = 640, model_size: str = 's'):
    """
    Train YOLOv8 cho CCCD detection
    
    Args:
        data_yaml: Đường dẫn đến file data.yaml
        epochs: Số epochs
        imgsz: Kích thước ảnh
        model_size: Kích thước model ('n', 's', 'm', 'l', 'x')
    """
    
    # Kiểm tra GPU
    device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
    print("=" * 60)
    print(f"🔧 Device: {device}")
    if torch.cuda.is_available():
        print(f"🎮 GPU: {torch.cuda.get_device_name(0)}")
        print(f"💾 GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
    else:
        print("⚠️  CPU mode - Training sẽ RẤT CHẬM!")
        print("   Khuyến nghị: Dùng Google Colab với GPU miễn phí")
    print("=" * 60)
    
    # Kiểm tra data.yaml
    data_path = Path(data_yaml)
    if not data_path.exists():
        raise FileNotFoundError(f"❌ Không tìm thấy file: {data_yaml}")
    print(f"✓ Found data.yaml: {data_yaml}")
    
    # Load pretrained model
    model_name = f'yolov8{model_size}.pt'
    print(f"\n📦 Loading pretrained model: {model_name}")
    model = YOLO(model_name)
    print(f"✓ Model loaded!")
    
    # Training config
    batch_size = 16 if device == 'cuda:0' else 4
    workers = 8 if device == 'cuda:0' else 2
    
    print(f"\n🚀 Starting training...")
    print(f"   Epochs: {epochs}")
    print(f"   Image size: {imgsz}")
    print(f"   Batch size: {batch_size}")
    print(f"   Workers: {workers}")
    print("=" * 60)
    
    # Train
    results = model.train(
        # Dataset
        data=data_yaml,
        
        # Training parameters
        epochs=epochs,
        imgsz=imgsz,
        batch=batch_size,
        
        # Model saving - LƯU VÀO THƯ MỤC models/
        project=str(ROOT / 'models'),  # Lưu vào thư mục models/
        name='cccd_yolo',
        exist_ok=True,
        
        # Optimization
        patience=50,
        save=True,
        save_period=10,
        
        # Hardware
        device=device,
        workers=workers,
        
        # Data augmentation
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        degrees=0.0,
        translate=0.1,
        scale=0.5,
        flipud=0.0,
        fliplr=0.5,
        mosaic=1.0,
        
        # Verbosity
        verbose=True,
        plots=True,
    )
    
    print("\n" + "=" * 60)
    print("✅ TRAINING COMPLETED!")
    print("=" * 60)
    print(f"📁 Best model: {results.save_dir}/weights/best.pt")
    print(f"📁 Last model: {results.save_dir}/weights/last.pt")
    print(f"📊 Results: {results.save_dir}")
    print("=" * 60)
    
    return results

def validate_model(model_path: str, data_yaml: str):
    """Validate model trên validation set"""
    print(f"\n📊 Validating model: {model_path}")
    
    model = YOLO(model_path)
    metrics = model.val(data=data_yaml)
    
    print("\n" + "=" * 60)
    print("📈 VALIDATION METRICS")
    print("=" * 60)
    print(f"   mAP50:     {metrics.box.map50:.4f}")
    print(f"   mAP50-95:  {metrics.box.map:.4f}")
    print(f"   Precision: {metrics.box.mp:.4f}")
    print(f"   Recall:    {metrics.box.mr:.4f}")
    print("=" * 60)
    
    return metrics

if __name__ == "__main__":
    # CẤU HÌNH TRAINING
    
    # Đường dẫn data.yaml 
    DATA_YAML = str(ROOT / 'CCCD_Dataset' / 'data.yaml')
    
    # Training parameters
    EPOCHS = 100        # Số epochs (100-200 epochs cho tốt)
    IMG_SIZE = 640      # Kích thước ảnh (640 là tốt nhất)
    MODEL_SIZE = 's'    # 'n'=nano, 's'=small, 'm'=medium, 'l'=large, 'x'=xlarge
    
    # Kiểm tra dataset
    print("🔍 Checking dataset...")
    dataset_path = ROOT / 'CCCD_Dataset'
    if not dataset_path.exists():
        print(f"❌ KHÔNG TÌM THẤY dataset tại: {dataset_path}")
        print(f"   Vui lòng kiểm tra lại thư mục!")
        sys.exit(1)
    
    # Kiểm tra các thư mục con
    for folder in ['train', 'valid', 'test']:
        folder_path = dataset_path / folder
        if not folder_path.exists():
            print(f"⚠️  Cảnh báo: Không tìm thấy folder {folder}/")
        else:
            images_path = folder_path / 'images'
            labels_path = folder_path / 'labels'
            
            if images_path.exists() and labels_path.exists():
                n_images = len(list(images_path.glob('*.jpg'))) + len(list(images_path.glob('*.png')))
                n_labels = len(list(labels_path.glob('*.txt')))
                print(f"✓ {folder:5s}: {n_images} images, {n_labels} labels")
            else:
                print(f"⚠️  {folder:5s}: thiếu folder images/ hoặc labels/")
    
    print("\n" + "=" * 60)
    
    # Hỏi xác nhận
    response = input("Bắt đầu training? (y/n): ")
    if response.lower() != 'y':
        print("❌ Hủy training")
        sys.exit(0)
    
    # Train model
    try:
        results = train_yolo(
            data_yaml=DATA_YAML,
            epochs=EPOCHS,
            imgsz=IMG_SIZE,
            model_size=MODEL_SIZE
        )
        
        # Validate best model
        best_model_path = f"{results.save_dir}/weights/best.pt"
        validate_model(best_model_path, DATA_YAML)
        
        print("\n✅ Done! Model đã sẵn sàng để sử dụng.")
        
    except KeyboardInterrupt:
        print("\n⚠️  Training bị ngắt bởi user")
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()