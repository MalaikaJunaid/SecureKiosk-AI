from pydantic import BaseModel
from src.schemas.cv_schema import CVProcessResult
from src.schemas.ocr_schema import OCRResult
from src.schemas.privacy_schema import RedactionResult


class DocumentProcessingResponse(BaseModel):
    status: str
    cv_metrics: CVProcessResult
    ocr_metrics: OCRResult
    privacy_metrics: RedactionResult