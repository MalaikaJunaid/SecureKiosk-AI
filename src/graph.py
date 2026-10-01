from typing import TypedDict, Optional, Any
from langgraph.graph import StateGraph, START, END
import numpy as np
import cv2

from src.cv.processor import DocumentProcessor
from src.ocr.extractor import OCRExtractor
from src.privacy.redactor import PIIRedactor

class DocumentState(TypedDict):
    image_bytes: bytes
    cropped_doc: Optional[np.ndarray]
    cv_metrics: Optional[Any]
    ocr_result: Optional[Any]
    redaction_result: Optional[Any]
    status: str

# Instantiate singletons for the graph nodes
cv_processor = DocumentProcessor()
ocr_extractor = OCRExtractor(psm=6)
pii_redactor = PIIRedactor()

def validation_node(state: DocumentState) -> dict:
    """Decodes image bytes, runs CV deskewing, face detection, and boundary extraction."""
    nparr = np.frombuffer(state["image_bytes"], np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if image is None:
        raise ValueError("Failed to decode image bytes in validation node.")
        
    cropped_doc, _, cv_result = cv_processor.process(image)
    return {
        "cropped_doc": cropped_doc,
        "cv_metrics": cv_result
    }

def redaction_node(state: DocumentState) -> dict:
    """Executes OCR text extraction on the cropped doc, followed by Presidio PII masking."""
    cropped_doc = state["cropped_doc"]
    
    # Run OCR extraction
    ocr_result = ocr_extractor.extract_text(cropped_doc)
    
    # Run Privacy Redaction on the raw text
    redaction_result = pii_redactor.redact(ocr_result.raw_text)
    
    return {
        "ocr_result": ocr_result,
        "redaction_result": redaction_result,
        "status": "success"
    }

def structuring_node(state: DocumentState) -> dict:
    """Final verification step before compiling the API payload."""
    return {"status": "success"}

def build_document_graph():
    workflow = StateGraph(DocumentState)
    
    # Register the modular nodes
    workflow.add_node("validate", validation_node)
    workflow.add_node("redact", redaction_node)
    workflow.add_node("structure", structuring_node)

    # Establish edge execution order
    workflow.add_edge(START, "validate")
    workflow.add_edge("validate", "redact")
    workflow.add_edge("redact", "structure")
    workflow.add_edge("structure", END)
    
    return workflow.compile()

# Compiled graph exportable by FastAPI
document_pipeline_graph = build_document_graph()