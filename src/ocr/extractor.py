import os
from typing import List
import cv2
import numpy as np
import pytesseract
from dotenv import load_dotenv

from src.schemas.cv_schema import BoundingBox
from src.schemas.ocr_schema import ExtractedWord, OCRResult

load_dotenv()

# Configure custom binary path if defined in .env
tesseract_cmd = os.getenv("TESSERACT_CMD")
if tesseract_cmd:
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd


class OCRExtractor:
    def __init__(self, psm: int = 6):
        """
        psm 6: Assume a single uniform block of text.
        psm 3: Fully automatic page segmentation (useful for multi-column docs).
        """
        self.config = f"--oem 3 --psm {psm}"

    @staticmethod
    def preprocess_for_ocr(image: np.ndarray) -> np.ndarray:
        """
        Applies localized adaptive thresholding to strip out complex 
        background watermarks and guilloche patterns from identity documents.
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()

        # Gaussian Blur removes high-frequency noise without destroying edges
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Adaptive Gaussian Thresholding to isolate dark text on varying backgrounds
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, blockSize=11, C=2           
        )
        
        # Morphological Closing to reconnect fragmented text strokes
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        processed_img = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        return processed_img

    def extract_text(self, image: np.ndarray) -> OCRResult:
        """
        Executes OCR on an image and returns structured words and confidence levels.
        """
        preprocessed = self.preprocess_for_ocr(image)

        # Retrieve detailed tabular token data
        data = pytesseract.image_to_data(
            preprocessed, config=self.config, output_type=pytesseract.Output.DICT
        )

        extracted_words: List[ExtractedWord] = []
        confidences: List[float] = []

        total_entries = len(data["text"])
        for i in range(total_entries):
            token = data["text"][i].strip()
            conf = float(data["conf"][i])

            # Filter empty strings and invalid confidence scores (-1)
            if token and conf >= 0:
                bbox = BoundingBox(
                    x=int(data["left"][i]),
                    y=int(data["top"][i]),
                    width=int(data["width"][i]),
                    height=int(data["height"][i]),
                )
                extracted_words.append(
                    ExtractedWord(text=token, confidence=conf, bbox=bbox)
                )
                confidences.append(conf)

        raw_text = " ".join([word.text for word in extracted_words]).strip()
        mean_conf = float(np.mean(confidences)) if confidences else 0.0

        return OCRResult(
            raw_text=raw_text,
            words=extracted_words,
            mean_confidence=round(mean_conf, 2),
            word_count=len(extracted_words),
            is_empty=(len(extracted_words) == 0),
        )