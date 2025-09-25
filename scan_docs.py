# file: img_scanner_with_cnn.py
import os
import json
import cv2
import numpy as np
import pytesseract.pytesseract as ptes
import torch
import torch.nn as nn
import torch.nn.functional as F
import matplotlib.pyplot as plt

ptes.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # оставь свой путь

#Путь к сохранённой модели
MODEL_PATH = r"C:\Users\us3r02\PycharmProjects\CNN_numbers_model\Pytorch_models\conv_net_model_X.ckpt"

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

    # Среднее: если фон тёмный (avg < 127), инвертируем, чтобы цифра была белой на чёрном (MNIST - белое на чёрном?):
    # MNIST pixels: фон ~0 (black) and digit lighter. Но в обучении мы нормализуем изображения как в MNIST (0..1).
    # Наш pipeline ниже сделает: будем приводить так, чтобы цифра была белой (1.0) и фон 0.0.
    mean_val = np.mean(gray)
    if mean_val > 127:
        # фон светлый (обычно фон 255), цифра темная -> инвертировать чтобы соответствовать MNIST (digit bright)
        img = 255 - gray
    else:
        img = gray.copy()

    # Ресайз в 28x28
    img = cv2.resize(img, (28, 28), interpolation=cv2.INTER_AREA)

    # Нормализация: приводим к [0,1]
    img = img.astype(np.float32) / 255.0

    # Нормализация по MNIST статистике (как у трансформов в обучении)
    # среднее 0.1307, std 0.3081 (если ты обучал с этими значениями)
    img = (img - 0.1307) / 0.3081

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

# -----------------------
# ImgScaner (интеграция CNN)
# -----------------------
class ImgScaner():
    def __init__(self, photo_path: str, ocr_mode='cnn'):
        """
        ocr_mode: 'cnn' или 'tesseract' — выбор движка для полей 'rate'
        """
        self.photo_path = photo_path
        self.ocr_mode = ocr_mode
        self.cnn = load_cnn_model() if ocr_mode == 'cnn' else None
        self.img = self.get_img()
        self.areas = self.get_ROIs()

    def get_ROIs(self):
        with open(r'ROIs.json', 'r', encoding='utf-8') as file:
            areas = json.load(file)
        return areas

    def correct_data(self, text):
        corrections = {
            "O": "0", "o": "0", "О": "0", "о": "0",  # буква O → ноль
            "I": "1", "l": "1", "|": "1",  # I/L/| → 1
            # не меняем x->х здесь: CNN вернёт 'X' как метку
        }
        for bad, good in corrections.items():
            text = text.replace(bad, good)
        return text

    def get_img(self):
        # читаем картинку
        img = cv2.imread(self.photo_path)
        if img is None:
            raise FileNotFoundError(f"Image not found: {self.photo_path}")

        # серое изображение (будем хранить grayscale чтобы ROI меньше занимали памяти)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # ресайз для стабильности (если нужно) — можно убрать/подогнать под свой сценарий
        # gray = cv2.resize(gray, (1920, 1080), interpolation=cv2.INTER_CUBIC)

        # лёгкое сглаживание (меньше мелких шумов)
        blur = cv2.GaussianBlur(gray, (3, 3), 0)

        # бинаризация (чёрный текст на белом фоне)
        thresh = cv2.adaptiveThreshold(
            blur, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 31, 2
        )

        # чистая версия (мягкое Opening) — на случай, если нужен бинарный вариант
        kernel = np.ones((2, 2), np.uint8)
        clean = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

        # вернём оригинал (gray) — но при get_roi можно выбрать нужный вариант
        return gray

    def get_text_from_img(self, img, mode, digits_only=False):
        """
        Оставлена совместимость: mode 'rate' = поля оценок; mode 'id' = id поля.
        Если self.ocr_mode == 'cnn' и mode == 'rate', используется CNN.
        """
        # Если для оценок выбран cnn — используем predict_with_cnn
        if mode == 'rate' and self.ocr_mode == 'cnn' and self.cnn is not None:
            label, conf = predict_with_cnn(self.cnn, img)
            # Вернём текст и, при желании, confidence (здесь просто текст)
            return label if label is not None else ""
        # Иначе fallback на tesseract
        config = ""
        if mode == 'rate':
            config += "--psm 8 --oem 1"
        elif mode == 'id':
            config += " --psm 7 --oem 3"

        if digits_only:
            config += " -c tessedit_char_whitelist=0123456789"

        text = ptes.image_to_string(img, config=config, lang="rus+eng")
        return text

    def get_roi(self, roi_name, work_n=-1, inner_offset=6):
        """
        Возвращает ROI из серого изображения self.img
        inner_offset — отступ внутрь прямоугольника, чтобы не захватить рамки
        """
        if work_n > -1:
            x, y, w, h = self.areas[f'work{work_n}'][roi_name]
        else:
            x, y, w, h = self.areas[roi_name]

        # защита на границы
        x1 = max(0, x + inner_offset)
        y1 = max(0, y + inner_offset)
        x2 = max(x1 + 1, x + w - inner_offset)
        y2 = max(y1 + 1, y + h - inner_offset)

        roi = self.img[y1:y2, x1:x2].copy()
        return roi

    def get_structure_data(self):
        k_work = 6
        k_numb = 6

        roi_exp = self.get_roi('id_exp')
        id_exp = self.get_text_from_img(roi_exp, 'id', digits_only=True).replace('\n', '')

        result = [id_exp, dict()]

        for work_n in range(1, k_work):  # перебор работ на листе
            work_id_roi = self.get_roi('id', work_n=work_n)

            work_id_text = self.get_text_from_img(work_id_roi, 'id', digits_only=True).replace('\n', '')
            result[1][work_id_text] = {f'{n}': None for n in range(1, k_numb + 1)}

            for numb in range(1, k_numb + 1):  # перебор номеров для каждого уч
                numb_roi = self.get_roi(f'{numb}', work_n=work_n)

                # если режим CNN — получаем метку через сеть
                if self.ocr_mode == 'cnn':
                    label, conf = predict_with_cnn(self.cnn, numb_roi)
                    rate = label if label is not None else ""
                else:
                    rate = self.correct_data(self.get_text_from_img(numb_roi, 'rate').replace('\n', ''))

                result[1][work_id_text][f'{numb}'] = rate

                # сохраняем ROI для отладки
                if not os.path.exists(f"nums/{id_exp}"):
                    os.makedirs(f"nums/{id_exp}", mode=0o777, exist_ok=True)
                cv2.imwrite(f'nums/{id_exp}/{work_n}_{numb}.jpg', numb_roi)
        print(result)
        return result


# -----------------------
# Точка входа
# -----------------------
def main():
    all_scans_data = []
    k_scans = 2

    for n_file in range(1, k_scans + 1):
        file_path = rf"scans\{n_file}.jpg"
        scan_object = ImgScaner(file_path, ocr_mode='cnn')  # либо 'tesseract'
        all_scans_data.append(scan_object.get_structure_data())

    print(all_scans_data)
    return all_scans_data


if __name__ == "__main__":
    main()
