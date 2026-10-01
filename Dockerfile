# Use official lean Python image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Install system-level dependencies for OpenCV and Tesseract
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download the spaCy language model required by Presidio
RUN python -m spacy download en_core_web_lg


# Copy the microservice source code
COPY src/ ./src/

# Expose the API port
EXPOSE 8000

# Start the Uvicorn ASGI server
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]