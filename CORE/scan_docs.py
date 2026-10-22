"""Read a fixed-layout protocol using Tesseract IDs and CNN scores."""

from abc import ABC, abstractmethod
import json
from pathlib import Path

import cv2
import numpy as np
import pytesseract

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROIS = ROOT / "data" / "ROIs.json"


class BaseOCR(ABC):
    @abstractmethod
    def recognize(self, image):
        raise NotImplementedError


class TesseractOCR(BaseOCR):
    def __init__(self, digits_only=False):
        self.digits_only = digits_only

    def recognize(self, image):
        config = "--psm 7 --oem 3"
        if self.digits_only:
            config += " -c tessedit_char_whitelist=0123456789"
        return pytesseract.image_to_string(image, config=config, lang="eng").strip()


class CNNOCR(BaseOCR):
    def __init__(self, model_path):
        from CNNModel.model import load_model
        self.model = load_model(model_path)

    def recognize(self, image):
        import torch
        from CNNModel.model import CLASS_MAP
        tensor = preprocess_for_cnn(image)
        with torch.no_grad():
            index = self.model(tensor).argmax(dim=1).item()
        return CLASS_MAP[index]


def preprocess_for_cnn(image):
    import torch
    if image.size == 0:
        raise ValueError("Cannot recognize an empty image region")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image.copy()
    h, w = gray.shape
    pad = max(1, int(min(h, w) * 0.05))
    if h > 2 * pad and w > 2 * pad:
        gray = gray[pad:h-pad, pad:w-pad]
    if np.mean(gray) > 127:
        gray = 255 - gray
    image = cv2.resize(gray, (28, 28), interpolation=cv2.INTER_AREA)
    normalized = (image.astype(np.float32) / 255.0 - 0.1307) / 0.3081
    return torch.from_numpy(normalized).unsqueeze(0).unsqueeze(0)


def load_image(path):
    # imdecode handles non-ASCII paths on Windows as well as POSIX paths.
    data = np.fromfile(path, dtype=np.uint8)
    if not data.size:
        raise ValueError(f"Empty image file: {path}")
    try:
        image = cv2.imdecode(data, cv2.IMREAD_GRAYSCALE)
    except cv2.error as error:
        raise ValueError(f"Cannot read image: {path}") from error
    if image is None:
        raise ValueError(f"Cannot read image: {path}")
    return image


def crop_roi(image, coords, offset=6):
    if (not isinstance(coords, list) or len(coords) != 4
            or any(type(value) is not int for value in coords)):
        raise ValueError(f"Invalid ROI coordinates: {coords!r}")
    x, y, width, height = coords
    image_height, image_width = image.shape[:2]
    if (x < 0 or y < 0 or width <= 2*offset or height <= 2*offset
            or x + width > image_width or y + height > image_height):
        raise ValueError(f"ROI {coords!r} is outside the image or too small")
    return image[y+offset:y+height-offset, x+offset:x+width-offset]


class ImgScanner:
    def __init__(self, image_path, ocr_mode, rois_path=DEFAULT_ROIS, work_count=6):
        if not 1 <= work_count <= 10:
            raise ValueError("work_count must be between 1 and 10")
        self.img = load_image(image_path)
        self.ocr = ocr_mode
        self.id_ocr = TesseractOCR(digits_only=True)
        with Path(rois_path).open(encoding="utf-8") as source:
            self.areas = json.load(source)
        self.work_count = work_count

    def get_roi(self, roi_name, work_n=-1):
        area = self.areas[f"work{work_n}"] if work_n > -1 else self.areas
        if roi_name not in area:
            raise ValueError(f"Missing ROI {roi_name!r} for work {work_n}")
        return crop_roi(self.img, area[roi_name])

    @staticmethod
    def _normalize_text(text):
        for bad, good in {"O": "0", "o": "0", "О": "0", "о": "0", "I": "1", "l": "1", "|": "1"}.items():
            text = text.replace(bad, good)
        return text.strip()

    def get_structure_data(self):
        expert = self._normalize_text(self.id_ocr.recognize(self.get_roi("id_exp")))
        works = {}
        for work in range(1, self.work_count + 1):
            work_id = self._normalize_text(self.id_ocr.recognize(self.get_roi("id", work)))
            if work_id in works:
                raise ValueError(f"Duplicate recognized work ID {work_id!r}; check image and ROI")
            works[work_id] = [self.ocr.recognize(self.get_roi(str(n), work)) for n in range(1, 7)]
        return {"expert_id": expert, "works": works}
