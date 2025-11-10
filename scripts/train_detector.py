"""
Script để train YOLOv8 model
"""
from ultralytics import YOLO

def train_yolo(data_yaml: str, epochs: int = 100, imgsz: int = 640):
    # Load pretrained model
    model = YOLO('yolov8n.pt')
    
    # Train
    results = model.train(
        data=data_yaml,
        epochs=epochs,
        imgsz=imgsz,
        patience=50,
        batch=16,
        device='cpu',  # Change to 'cuda:0' if using GPU
        project='models/detection',
        name='yolov8_id_card',
        exist_ok=True
    )
    
    print("Training completed!")
    print(f"Best model saved at: {results.save_dir}")

if __name__ == "__main__":
    train_yolo('data/processed/data.yaml', epochs=100)