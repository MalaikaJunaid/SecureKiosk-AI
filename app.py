import streamlit as st
import numpy as np
import cv2
from PIL import Image, ImageDraw

from src.graph import document_pipeline_graph

st.set_page_config(page_title="SecureKiosk AI", page_icon="🛡️", layout="wide")

st.title("🛡️️ SecureKiosk AI: Privacy-Preserving Document Pipeline")
st.markdown("Enterprise-grade pipeline featuring local CV bounding, OCR, and zero-trust PII redaction.")
st.divider()

uploaded_file = st.file_uploader("Upload an Identity Document (PNG/JPG)", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # Read raw bytes and convert to PIL Image for display
    file_bytes = uploaded_file.getvalue()
    image = Image.open(uploaded_file).convert("RGB")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Original Document")
        st.image(image, width="stretch")

    with col2:
        st.subheader("Pipeline Analysis")
        if st.button("Process Document Securely", type="primary"):
            with st.spinner("Executing LangGraph pipeline (CV -> OCR -> PII Redaction)..."):
                initial_state = {
                    "image_bytes": file_bytes,
                    "cropped_doc": None,
                    "cv_metrics": None,
                    "ocr_result": None,
                    "redaction_result": None,
                    "status": "pending"
                }
                
                try:
                    final_state = document_pipeline_graph.invoke(initial_state)
                    
                    if final_state.get("status") == "success":
                        st.success("Document Processed & Redacted Successfully!")
                        
                        cv_metrics = final_state.get("cv_metrics")
                        ocr_metrics = final_state.get("ocr_result")
                        privacy_metrics = final_state.get("redaction_result")
                        
                        # Helper extractor for objects or dicts
                        def get_val(obj, key, default=None):
                            if obj is None:
                                return default
                            if isinstance(obj, dict):
                                return obj.get(key, default)
                            return getattr(obj, key, default)

                        # 1. Computer Vision Results & Visual Face Bounding Box
                        face_detected = get_val(cv_metrics, "face_detected", False)
                        face_bbox = get_val(cv_metrics, "face_bbox")
                        
                        if face_detected and face_bbox:
                            st.success(f"Face detected at: {face_bbox}")
                            annotated_image = image.copy()
                            draw = ImageDraw.Draw(annotated_image)
                            
                            bx = get_val(face_bbox, "x", 0)
                            by = get_val(face_bbox, "y", 0)
                            bw = get_val(face_bbox, "width", 0)
                            bh = get_val(face_bbox, "height", 0)
                            
                            draw.rectangle(
                                [bx, by, bx + bw, by + bh],
                                outline="red",
                                width=5
                            )
                            st.image(annotated_image, caption="Isolated Region of Interest", width="stretch")
                        else:
                            st.warning("No face detected in document")

                        # 2. PII Redaction Results
                        st.subheader("Redacted Text (Masked PII)")
                        redacted_text = get_val(privacy_metrics, "redacted_text")
                        if not redacted_text:
                            redacted_text = getattr(privacy_metrics, "text", "No text extracted")
                        
                        st.info(redacted_text)
                        
                        st.markdown("**Entities Masked:**")
                        redacted_entities = get_val(privacy_metrics, "redacted_entities", {})
                        st.write(redacted_entities)

                        # 3. Raw Inspection Data
                        with st.expander("Inspect Raw Pipeline State"):
                            st.write({
                                "status": final_state.get("status"),
                                "cv_metrics": cv_metrics,
                                "ocr_metrics": ocr_metrics,
                                "privacy_metrics": privacy_metrics
                            })
                    else:
                        st.error("Pipeline failed to process the document.")
                        
                except Exception as e:
                    st.error(f"Pipeline Execution Error: {e}")