import os
import requests

# FastAPI local server endpoint
URL = "http://127.0.0.1:8000/api/v1/process"

# Select one of your sample documents to test
sample_image_path = "samples/img_dl.png"  # Change to any file in your samples folder

def run_test():
    if not os.path.exists(sample_image_path):
        print(f"Sample image not found at {sample_image_path}. Please check your path.")
        return

    print(f"-> Sending {sample_image_path} to SecureKiosk-AI pipeline...")

    with open(sample_image_path, "rb") as f:
        files = {"file": (os.path.basename(sample_image_path), f, "image/jpeg")}
        try:
            response = requests.post(URL, files=files)
            
            print(f"\nStatus Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("\n Pipeline Execution Successful!")
                print(f"• Processing Status: {data.get('status')}")
                print(f"• CV Document Detected: {data.get('cv_metrics', {}).get('document_detected')}")
                print(f"• CV Face Detected: {data.get('cv_metrics', {}).get('face_detected')}")
                print(f"• OCR Word Count: {data.get('ocr_metrics', {}).get('word_count')}")
                print(f"• OCR Mean Confidence: {data.get('ocr_metrics', {}).get('mean_confidence')}%")
                print(f"• Redacted Entities Found: {list(data.get('privacy_metrics', {}).get('redacted_entities', {}).keys())}")
            else:
                print(f"\n Error Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("\n Could not connect to the FastAPI server. Make sure it is running (uvicorn src.api.main:app --reload).")

if __name__ == "__main__":
    run_test()