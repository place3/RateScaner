# file: img_scanner_with_cnn.py
import os
import json
import cv2
import numpy as np
import pytesseract.pytesseract as ptes
import torch
import torch.nn as nn
from CNNModel.numsAndX import predict_symbol
import torch.nn.functional as F
import matplotlib.pyplot as plt

ptes.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # оставь свой путь

#Путь к сохранённой модели
MODEL_PATH = r"C:\Users\us3r02\PycharmProjects\CNN_numbers_model\Pytorch_models\best_conv_net_model_X.pth"

#Мэппинг выходов сети в строки
CLASS_MAP = ['0', '1', '2', '3', '4', 'X']  # индекс -> метка

# -----------------------
# Определение архитектуры (должна совпадать с обученной)
# -----------------------
class ConvNet(nn.Module):
    def __init__(self):
        super(ConvNet, self).__init__()
        self.layer1 = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=5, stride=1, padding=2),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2)
        )
        self.layer2 = nn.Sequential(
            nn.Conv2d(32, 64, kernel_size=5, stride=1, padding=2),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2)
        )
        self.drop_out = nn.Dropout()
        self.fc1 = nn.Linear(7 * 7 * 64, 1000)
        self.fc2 = nn.Linear(1000, 6)  # 6 классов

    def forward(self, x):
        out = self.layer1(x)
        out = self.layer2(out)
        out = out.reshape(out.size(0), -1)
        out = self.drop_out(out)
        out = self.fc1(out)
        out = self.fc2(out)
        return out

# -----------------------
# Утилиты для CNN
# -----------------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def load_cnn_model(path=MODEL_PATH):
    model = ConvNet()
    if os.path.exists(path):
        state = torch.load(path, map_location=device)
        model.load_state_dict(state)
        model.to(device)
        model.eval()
        print(f"[INFO] Loaded model from {path} to {device}")
    else:
        print(f"[WARN] Model file not found at {path}. CNN will not work until you provide it.")
    return model

def preprocess_for_cnn(roi):
    """
    roi: numpy array (ROI) — может быть grayscale или BGR
    Возвращает тензор shape [1,1,28,28] dtype=torch.float32 на том же device
    Предобработка: grayscale -> инверсия при необходимости -> resize 28x28 -> нормализация (MNIST stats)
    """
    if len(roi.shape) == 3:
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    else:
        gray = roi.copy()

    # Убираем рамки: немного внутwренняя обрезка (если вокруг рамка)
    h, w = gray.shape
    pad = max(1, int(min(h, w) * 0.05))  # 5% по-умолчанию
    gray = gray[pad:h - pad, pad:w - pad] if (h > 2*pad and w > 2*pad) else gray

    mean_val = np.mean(gray)
    if mean_val > 127:
        # фон светлый (обычно фон 255), цифра темная -> инвертировать чтобы соответствовать MNIST (digit bright)
        img = 255 - gray
    else:
        img = gray.copy()

    img = cv2.resize(img, (28, 28), interpolation=cv2.INTER_AREA)

    # Нормализация: приводим к [0,1]
    img = img.astype(np.float32) / 255.0
    # Нормализация по MNIST статистике (как у трансформов в обучении)
    img = (img - 0.1307) / 0.3081
    # cv2.imshow('f', img)
    # cv2.waitKey(0)
    tensor = torch.from_numpy(img).unsqueeze(0).unsqueeze(0).to(device)  # [1,1,28,28]
    return tensor

def predict_with_cnn(model, roi):
    """
    Возвращает (label_str, confidence_float)
    """
    if model is None:
        return None, 0.0
    tensor = preprocess_for_cnn(roi)
    with torch.no_grad():
        out = model(tensor)  # [1, num_classes]
        probs = torch.softmax(out, dim=1).cpu().numpy().squeeze()
        idx = int(np.argmax(probs))
        conf = float(probs[idx])
        return CLASS_MAP[idx], conf


#Интерфейс для ORC
from abc import ABC, abstractmethod

class BaseOCR(ABC):
    """Интерфейс OCR"""
    @abstractmethod
    def recognize(self, image):
        pass

class TesseractOCR(BaseOCR):
    """Реализация OCR через Tesseract"""
    def __init__(self, digits_only=False):
        self.digits_only = digits_only

    def recognize(self, image):
        config = "--psm 7 --oem 3 "
        if self.digits_only:
            config += " -c tessedit_char_whitelist=0123456789"
        text = ptes.image_to_string(image, config=config, lang="rus+eng").strip()
        return text

class CNNOCR(BaseOCR):
    """Реализация OCR через нейросеть"""
    def __init__(self):
        self.model = load_cnn_model()

    def recognize(self, image, rate = True):

        label, _ = predict_with_cnn(self.model, image)
        return label

#Обработка изображений
def load_image(path):
    img = cv2.imread(path)
    if img is None:
        raise FileNotFoundError(f"Image not found: {path}")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    thresh = cv2.adaptiveThreshold(
        blur, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 31, 2
    )
    kernel = np.ones((2, 2), np.uint8)
    clean = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    return gray


def crop_roi(img, coords, offset=6):
    x, y, w, h = coords
    x1, y1 = x + offset, y + offset
    x2, y2 = x + w - offset, y + h - offset
    return img[y1:y2, x1:x2]

# -----------------------
# ImgScaner (интеграция CNN)
# -----------------------


class ImgScanner:
    def __init__(self,
                 image_path: str,
                 ocr_mode: BaseOCR,
                 rois_path: str = r"C:\Users\us3r02\PycharmProjects\ege_doc_scan\ROIs.json"
                 ):
        self.image_path = image_path
        self.ocr = ocr_mode
        self.img = load_image(image_path)
        self.areas = self._load_rois(rois_path)

        # Конфигурационные параметры
        self.k_work = 6  # количество работ
        self.k_numb = 6  # количество оценок в каждой работе

    # -----------------------
    # Загрузка ROI из JSON
    # -----------------------
    def _load_rois(self, path: str) -> dict:
        """Загружает координаты ROI из JSON"""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Файл ROI не найден: {path}")
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    # -----------------------
    # Работа с ROI
    # -----------------------
    def get_roi(self, roi_name: str, work_n: int = -1):
        if work_n > -1:
            coords = self.areas[f'work{work_n}'][roi_name]
        else:
            coords = self.areas[roi_name]
        return crop_roi(self.img, coords)


    def _normalize_text(self, text: str) -> str:
        """Заменяет часто путаемые символы"""
        corrections = {
            "O": "0", "o": "0", "О": "0", "о": "0",
            "I": "1", "l": "1", "|": "1"
        }
        for bad, good in corrections.items():
            text = text.replace(bad, good)
        return text

    # -----------------------
    # Распознавание данных
    # -----------------------
    def get_structure_data(self):
        """
        Основной метод:
        - распознаёт ID эксперимента
        - для каждой работы получает ID и оценки
        - возвращает структурированные данные
        """
        # 1️⃣ Распознаём id эксперта
        exp_roi = self.get_roi("id_exp")
        id_exp = self._normalize_text(TesseractOCR(digits_only=True).recognize(image = exp_roi))
        result = [id_exp, {}]

        # 2️⃣ Для каждой работы
        for work_n in range(1, self.k_work + 1):
            work_id_roi = self.get_roi("id", work_n)
            work_id = self._normalize_text(TesseractOCR(digits_only=True).recognize(work_id_roi))
            result[1][work_id] = {}
            # cv2.imshow('f', work_id_roi)
            # cv2.waitKey(0)
            # 3️⃣ Для каждой оценки
            for numb in range(1, self.k_numb + 1):
                rate_roi = self.get_roi(str(numb), work_n)
                rate = self._normalize_text(self.ocr.recognize(rate_roi))
                # cv2.imshow('f', rate_roi)
                # cv2.waitKey(0)
                result[1][work_id][str(numb)] = rate

        return result

    # -----------------------
    # Сохранение ROI (для отладки)
    # -----------------------
    def save_rois(self, output_dir: str = "debug_rois"):
        """Сохраняет все вырезанные ROI на диск"""
        os.makedirs(output_dir, exist_ok=True)
        for work_n in range(1, self.k_work + 1):
            for n in range(1, self.k_numb + 1):
                roi = self.get_roi(str(n), work_n)
                cv2.imwrite(f"{output_dir}/work{work_n}_{n}.jpg", roi)


# -----------------------
# Точка входа
# -----------------------
def main():
    all_scans_data = []
    k_scans = 2

    for n_file in range(1, k_scans + 1):
        file_path = rf"scans\{n_file}.jpg"
        scan_object = ImgScanner(file_path, ocr_mode=CNNOCR())  # либо 'tesseract'
        all_scans_data.append(scan_object.get_structure_data())

    print(all_scans_data)
    return all_scans_data


if __name__ == "__main__":
    main()
