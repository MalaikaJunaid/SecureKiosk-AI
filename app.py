import streamlit as st
import requests
from PIL import Image, ImageDraw

# Pointing to the active Kubernetes LoadBalancer / port-forward tunnel
API_URL = "http://localhost:8000/api/v1/process"

st.set_page_config(page_title="SecureKiosk AI", page_icon="🛡️", layout="wide")

st.title("🛡️ SecureKiosk AI: Privacy-Preserving Document Pipeline")
st.markdown("Enterprise-grade pipeline featuring local CV bounding, OCR, and zero-trust PII redaction.")
st.divider()

uploaded_file = st.file_uploader("Upload an Identity Document (PNG/JPG)", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Original Document")
        st.image(image, use_container_width=True)

    with col2:
        st.subheader("Pipeline Analysis")
        if st.button("Process Document Securely", type="primary"):
            with st.spinner("Executing CV and NLP models..."):
                uploaded_file.seek(0)
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "image/jpeg")}
                
                try:
                    response = requests.post(API_URL, files=files, timeout=60)
                    response.raise_for_status()
                    result = response.json()
                    
                    # 1. Computer Vision Results
                    cv = result.get("cv_metrics", {})
                    if cv.get("face_detected"):
                        st.success(f"Face detected at: {cv.get('face_bbox')}")
                        
                        annotated_image = image.copy()
                        draw = ImageDraw.Draw(annotated_image)
                        box = cv["face_bbox"]
                        draw.rectangle(
                            [box["x"], box["y"], box["x"] + box["width"], box["y"] + box["height"]],
                            outline="red",
                            width=5
                        )
                        st.image(annotated_image, caption="Isolated Region of Interest", use_container_width=True)
                    else:
                        st.warning("No face detected in document")

                    # 2. PII Redaction Results
                    st.subheader("Redacted Text (Masked PII)")
                    privacy = result.get("privacy_metrics", {})
                    st.info(privacy.get("redacted_text", "No text extracted"))
                    
                    st.markdown("**Entities Masked:**")
                    st.write(privacy.get("redacted_entities", {}))

                    # 3. Raw Inspection Data
                    with st.expander("Inspect Raw Response"):
                        st.json(result)
                        
                except requests.exceptions.RequestException as e:
                    st.error(f"API Connection Error: {e}")
                    st.info("Ensure your cluster tunnel is running: `kubectl port-forward svc/securekiosk-service 8000:80`")