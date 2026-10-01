from typing import List, Optional
from pydantic import BaseModel, Field
from src.schemas.cv_schema import BoundingBox


class ExtractedWord(BaseModel):
    text: str = Field(..., description="Detected word token")
    confidence: float = Field(..., description="OCR confidence score (0-100)")
    bbox: BoundingBox = Field(..., description="Word bounding coordinates")


class OCRResult(BaseModel):
    raw_text: str = Field(..., description="Full concatenated text extracted from image")
    words: List[ExtractedWord] = Field(default_factory=list, description="Structured tokens with coordinates")
    mean_confidence: float = Field(..., description="Average confidence score across tokens")
    word_count: int = Field(..., description="Total extracted tokens")
    is_empty: bool = Field(..., description="Indicates if no readable text was detected")