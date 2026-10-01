from fastapi import FastAPI, UploadFile, File, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator

from src.graph import document_pipeline_graph
from src.schemas.api_schema import DocumentProcessingResponse

# 1. Initialize FastAPI
app = FastAPI(
    title="SecureKiosk AI",
    description="Privacy-Preserving Document & Identity Pipeline",
    version="1.0.0"
)
Instrumentator().instrument(app).expose(app)

@app.get("/healthz")
async def health_check():
    """Kubernetes liveness/readiness probe endpoint."""
    return {"status": "healthy"}

@app.post("/api/v1/process", response_model=DocumentProcessingResponse)
async def process_document(file: UploadFile = File(...)):
    """
    End-to-end stateful agentic pipeline via LangGraph:
    1. Reads image upload bytes.
    2. Invokes graph state machine (CV -> OCR -> Privacy Redaction).
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")

    try:
        contents = await file.read()
        
        # Initialize the LangGraph state payload
        initial_state = {
            "image_bytes": contents,
            "cropped_doc": None,
            "cv_metrics": None,
            "ocr_result": None,
            "redaction_result": None,
            "status": "pending"
        }
        
        # Execute the stateful graph workflow
        final_state = document_pipeline_graph.invoke(initial_state)

        # Return structured API response matching schema
        return DocumentProcessingResponse(
            status=final_state["status"],
            cv_metrics=final_state["cv_metrics"],
            ocr_metrics=final_state["ocr_result"],
            privacy_metrics=final_state["redaction_result"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))