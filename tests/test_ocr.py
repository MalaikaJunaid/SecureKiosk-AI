import cv2
import numpy as np
import pytest
from src.ocr.extractor import OCRExtractor


@pytest.fixture
def extractor():
    return OCRExtractor(psm=6)


@pytest.fixture
def synthetic_text_image():
    # Create white canvas
    canvas = np.ones((150, 600, 3), dtype=np.uint8) * 255
    # Render crisp black text
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(canvas, "IDENTITY CARD", (50, 80), font, 1.4, (0, 0, 0), 3, cv2.LINE_AA)
    return canvas


def test_ocr_extracts_synthetic_text(extractor, synthetic_text_image):
    result = extractor.extract_text(synthetic_text_image)
    assert not result.is_empty
    assert "IDENTITY" in result.raw_text.upper()
    assert "CARD" in result.raw_text.upper()
    assert result.mean_confidence > 50.0
    assert result.word_count >= 2


def test_ocr_blank_image(extractor):
    blank = np.ones((100, 100, 3), dtype=np.uint8) * 255
    result = extractor.extract_text(blank)
    assert result.is_empty
    assert result.word_count == 0
    assert result.raw_text == ""
    assert result.mean_confidence == 0.0