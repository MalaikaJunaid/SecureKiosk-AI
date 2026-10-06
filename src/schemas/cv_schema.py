from typing import Optional, Tuple
from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    x: int = Field(..., description="Top-left X coordinate")
    y: int = Field(..., description="Top-left Y coordinate")
    width: int = Field(..., description="Width of detected region")
    height: int = Field(..., description="Height of detected region")


class CVProcessResult(BaseModel):
    document_detected: bool = Field(..., description="Whether document boundaries were found")
    deskewed: bool = Field(..., description="Whether perspective deskewing was applied")
    face_detected: bool = Field(..., description="Whether a face portrait was found")
    face_bbox: Optional[BoundingBox] = Field(None, description="Coordinates of detected face")
    original_dimensions: Tuple[int, int] = Field(..., description="(height, width) of input")
    processed_dimensions: Tuple[int, int] = Field(..., description="(height, width) of cropped document")