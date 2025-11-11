from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import sys
from pathlib import Path

# Thêm root vào sys.path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.pipeline.main_pipeline import IDCardPipeline

# Khởi tạo FastAPI
app = FastAPI(
    title="Vietnamese ID Card OCR API",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Khởi tạo Pipeline - BỎ config.config
pipeline = IDCardPipeline()  # ✅ ĐÚNG - Không truyền gì

@app.get("/")
def read_root():
    """Health check"""
    return {
        "message": "Vietnamese ID Card OCR API",
        "status": "running"
    }

@app.post("/api/process")
async def process_image(file: UploadFile = File(...)):
    """Xử lý ảnh CCCD/Bằng lái xe"""
    try:
        print("=" * 50)
        print("🔵 BẮT ĐẦU XỬ LÝ")
        
        # 1. Validate file type
        print(f"📁 File: {file.filename}")
        print(f"📁 Content-Type: {file.content_type}")
        
        if not file.content_type.startswith('image/'):
            raise HTTPException(400, "File phải là ảnh")
        
        # 2. Đọc file
        print("📖 Đang đọc file...")
        contents = await file.read()
        print(f"📖 Đã đọc {len(contents)} bytes")
        
        # 3. Decode ảnh
        print("🖼️  Đang decode ảnh...")
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            print("❌ cv2.imdecode trả về None!")
            raise HTTPException(400, "Không đọc được ảnh (decode failed)")
        
        print(f"✅ Decode thành công: {image.shape}")
        
        # 4. Process
        print("🔄 Đang xử lý với pipeline...")
        result = pipeline.process(image)
        
        print(f"✅ Xử lý xong: success={result.get('success')}")
        print("=" * 50)
        
        return result
        
    except HTTPException as he:
        print(f"⚠️  HTTPException: {he.detail}")
        raise
    except Exception as e:
        print(f"❌ Exception: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(500, f"Lỗi server: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting server at http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)