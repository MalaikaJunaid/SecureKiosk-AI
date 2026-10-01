from typing import Optional, Tuple
import cv2
import numpy as np

from src.schemas.cv_schema import BoundingBox, CVProcessResult


class DocumentProcessor:
    def __init__(self):
        # Load OpenCV's built-in frontal face detector
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

    @staticmethod
    def _order_points(pts: np.ndarray) -> np.ndarray:
        """
        Orders coordinates: top-left, top-right, bottom-right, bottom-left.
        """
        rect = np.zeros((4, 2), dtype="float32")
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]

        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        return rect

    def deskew_and_crop(self, image: np.ndarray) -> Tuple[np.ndarray, bool]:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(blurred, 50, 200)

        contours, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

        doc_contour = None
        image_area = image.shape[0] * image.shape[1]

        for c in contours:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            if len(approx) == 4:
                # NEW: Ensure the detected rectangle is at least 30% of the total image
                if cv2.contourArea(approx) > 0.3 * image_area:
                    doc_contour = approx
                    break

        if doc_contour is None:
            # Fall back to using the entire uncropped image
            return image, False

        pts = doc_contour.reshape(4, 2)
        rect = self._order_points(pts)
        (tl, tr, br, bl) = rect

        # Calculate width of new transformed image
        width_a = np.linalg.norm(br - bl)
        width_b = np.linalg.norm(tr - tl)
        max_width = max(int(width_a), int(width_b))

        # Calculate height of new transformed image
        height_a = np.linalg.norm(tr - br)
        height_b = np.linalg.norm(tl - bl)
        max_height = max(int(height_a), int(height_b))

        dst = np.array([
            [0, 0],
            [max_width - 1, 0],
            [max_width - 1, max_height - 1],
            [0, max_height - 1]
        ], dtype="float32")

        matrix = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(image, matrix, (max_width, max_height))
        return warped, True

    def extract_face(self, image: np.ndarray) -> Tuple[Optional[np.ndarray], Optional[BoundingBox]]:
        """
        Detects and extracts the primary face portrait from the document.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(60, 60)
        )

        if len(faces) == 0:
            return None, None

        # Pick the largest face area found
        x, y, w, h = max(faces, key=lambda b: b[2] * b[3])
        face_crop = image[y:y + h, x:x + w]
        bbox = BoundingBox(x=int(x), y=int(y), width=int(w), height=int(h))

        return face_crop, bbox

    
    @staticmethod
    def preprocess_for_ocr(image_bytes: bytes) -> np.ndarray:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, blockSize=11, C=2           
        )
        
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        return cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    def process(self, image: np.ndarray) -> Tuple[np.ndarray, Optional[np.ndarray], CVProcessResult]:
        """
        Pipeline runner: runs deskew and face extraction.
        """
        orig_h, orig_w = image.shape[:2]
        cropped_doc, deskewed = self.deskew_and_crop(image)
        proc_h, proc_w = cropped_doc.shape[:2]

        face_img, face_bbox = self.extract_face(cropped_doc)

        result = CVProcessResult(
            document_detected=deskewed,
            deskewed=deskewed,
            face_detected=(face_bbox is not None),
            face_bbox=face_bbox,
            original_dimensions=(orig_h, orig_w),
            processed_dimensions=(proc_h, proc_w)
        )

        return cropped_doc, face_img, result

    