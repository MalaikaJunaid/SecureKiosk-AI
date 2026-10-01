import numpy as np
import cv2
import pytest
from src.cv.processor import DocumentProcessor


@pytest.fixture
def processor():
    return DocumentProcessor()


@pytest.fixture
def synthetic_card_image():
    # 800x1200 canvas
    canvas = np.zeros((800, 1200, 3), dtype=np.uint8)
    # White card tilted/drawn inside canvas
    pts = np.array([[200, 150], [1000, 180], [980, 650], [180, 620]], np.int32)
    cv2.fillPoly(canvas, [pts], (255, 255, 255))
    return canvas


def test_cv_process_dimensions(processor, synthetic_card_image):
    cropped_doc, face_img, result = processor.process(synthetic_card_image)
    assert result.original_dimensions == (800, 1200)
    assert cropped_doc is not None
    assert isinstance(result.document_detected, bool)


def test_fallback_on_plain_image(processor):
    plain = np.ones((500, 500, 3), dtype=np.uint8) * 128
    cropped_doc, face_img, result = processor.process(plain)
    assert result.document_detected is False
    assert result.processed_dimensions == (500, 500)
    assert face_img is None