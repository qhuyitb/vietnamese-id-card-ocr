from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import cv2
import numpy as np
from pathlib import Path
import tempfile
import shutil

from src.pipeline.main_pipeline import IDCardPipeline
from src.utils.config import Config
from api.schemas.response import ProcessResponse

# Initialize
app = FastAPI(title="ID Card Detection API", version="1.0.0")
config = Config()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.get('api.cors_origins', ['*']),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize pipeline
pipeline = IDCardPipeline(config.config)

@app.get("/")
async def root():
    return {"message": "ID Card Detection API", "version": "1.0.0"}

@app.post("/api/process", response_model=ProcessResponse)
async def process_image(file: UploadFile = File(...)):
    """
    Upload và xử lý ảnh CCCD/Bằng lái xe
    """
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    
    try:
        # Process image
        result = pipeline.process(tmp_path)
        return ProcessResponse(**result)
    
    finally:
        # Cleanup
        Path(tmp_path).unlink(missing_ok=True)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host=config.get('api.host', '0.0.0.0'),
        port=config.get('api.port', 8000),
        reload=config.get('api.debug', True)
    )
