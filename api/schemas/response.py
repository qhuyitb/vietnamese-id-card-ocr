from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class DetectionResponse(BaseModel):
    bbox: List[int]
    confidence: float
    class_name: str

class OCRResult(BaseModel):
    text: str
    confidence: float

class ProcessResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    detection: Optional[DetectionResponse] = None
    full_text: Optional[str] = None
    parsed_data: Optional[Dict[str, Any]] = None
