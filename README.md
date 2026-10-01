# 🛡️ SecureKiosk-AI

>An enterprise-grade, privacy-preserving AI document and identity verification pipeline featuring localized computer vision preprocessing, stateful multi-agent orchestration, and zero-trust PII redaction.  # noqa: E999

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Stateful-orange.svg)](https://www.langchain.com/langgraph)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Minikube-326CE5.svg)](https://kubernetes.io/)
[![Docker](https://img.shields.io/badge/Docker-Multi--Stage-2496ED.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🚀 Overview

**SecureKiosk-AI** is a cloud-native, zero-trust document processing ecosystem engineered to securely extract, parse, and redact personally identifiable information (PII) from identity documents (driver's licenses, national ID cards, and passports). 

Traditional OCR pipelines struggle with complex background security graphics (like guilloche patterns and sun gradients) and pose severe data privacy risks. SecureKiosk-AI solves this by coupling **OpenCV adaptive thresholding** with an **agentic LangGraph state machine workflow** and **Microsoft Presidio** redaction, running inside a scalable Kubernetes cluster.

---

## 🏗️ Architecture & Workflow

The system coordinates modular processing engines through an orchestrated state machine graph:


```

[ Client Upload ] ---> [ FastAPI /api/v1/process ]
│
▼
[ LangGraph Orchestrator ]
│
┌─────────────────────┼─────────────────────┐
▼                     ▼                     ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  Validation Node │  │  Redaction Node  │  │ Structuring Node │
│  (OpenCV CV/Face)│  │ (Tesseract & PII)│  │ (Pydantic Models)│
└──────────────────┘  └──────────────────┘  └──────────────────┘

```

1. **Validation & Preprocessing Node (`src/cv/processor.py`)**: 
   - Decodes raw image payloads, executes perspective correction (deskewing), and extracts portrait bounding boxes via Haar Cascades.
   - Applies Gaussian blur and **adaptive Gaussian thresholding** (`cv2.adaptiveThreshold`) to strip out complex background watermarks while preserving text stroke edges.
2. **Extraction & Privacy Redaction Node (`src/ocr/extractor.py` & `src/privacy/redactor.py`)**:
   - Feeds clean binarized arrays into Tesseract OCR (`--oem 3 --psm 6`) to generate tabular token data and confidence scores.
   - Passes extracted text through Microsoft Presidio to detect and mask sensitive entities (e.g., `US_DRIVER_LICENSE`, `PERSON`, `LOCATION`, `DATE_TIME`).
3. **Structuring Node (`src/graph.py`)**:
   - Enforces strict Pydantic schemas before returning a JSON metrics payload to the API caller.

---

## 🛠️ Tech Stack

* **Backend & API**: Python, FastAPI, Pydantic, Uvicorn
* **Computer Vision & OCR**: OpenCV (`cv2`), PyTesseract, NumPy
* **Privacy & Security**: Microsoft Presidio Analyzer/Anonymizer
* **Orchestration**: LangGraph (Stateful Agentic Workflows)
* **DevOps & Infrastructure**: Docker (Multi-stage builds), Kubernetes (Minikube), Horizontal Pod Autoscaler (HPA), NGINX Ingress, Prometheus FastAPI Instrumentator

---

## 📂 Project Structure

```tree
SecureKiosk-AI/
├── k8s/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── hpa.yaml
│   └── ingress.yaml
├── samples/
│   ├── img_dl.png
│   ├── img_id.jpg
│   └── img_p.jpg
├── src/
│   ├── api/
│   │   └── main.py
│   ├── cv/
│   │   └── processor.py
│   ├── ocr/
│   │   └── extractor.py
│   ├── privacy/
│   │   └── redactor.py
│   ├── schemas/
│   │   ├── api_schema.py
│   │   ├── cv_schema.py
│   │   └── ocr_schema.py
│   └── graph.py
├── Dockerfile
├── requirements.txt
├── test_pipeline.py
└── README.md

```

---

## ⚙️ Getting Started Locally

### 1. Prerequisites

* Python 3.10+
* Tesseract OCR installed on your system path (or configured via `.env`)
* Docker & Minikube (optional, for local Kubernetes orchestration)

### 2. Installation

Clone the repository and set up a virtual environment:

```powershell
git clone [https://github.com/your-username/SecureKiosk-AI.git](https://github.com/your-username/SecureKiosk-AI.git)
cd SecureKiosk-AI
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

```

### 3. Running the FastAPI Server

Start the local API development server:

```powershell
uvicorn src.api.main:app --reload

```

### 4. Running End-to-End Tests

Execute the test script to push a sample document through the agentic pipeline:

```powershell
python test_pipeline.py

```

---

## ☸️ Kubernetes Deployment & Autoscaling

To deploy the containerized microservice to a local Kubernetes cluster with autoscaling and custom ingress traffic routing:

```powershell
# Apply deployment, service, HPA, and ingress manifests
kubectl apply -f k8s/

```

* **HPA (`k8s/hpa.yaml`)**: Automatically scales pods between 1 and 5 replicas based on a 70% CPU utilization threshold.
* **Ingress (`k8s/ingress.yaml`)**: Configures NGINX routing with an expanded body size allowance (`proxy-body-size: "15m"`) to support high-resolution ID uploads.
* **Monitoring (`/metrics`)**: Fully instrumented with `prometheus-fastapi-instrumentator` for production observability.

---

## 🛡️ License

Distributed under the MIT License. See `LICENSE` for more information.
