import cv2
import torch.nn as nn
import torch
from torchvision import transforms

num_classes = 6
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
        self.fc2 = nn.Linear(1000, num_classes)  # 6 классов

    def forward(self, x):
        out = self.layer1(x)
        out = self.layer2(out)
        out = out.reshape(out.size(0), -1)
        out = self.drop_out(out)
        out = self.fc1(out)
        out = self.fc2(out)
        return out

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = ConvNet().to(device)
model.load_state_dict(torch.load(r"C:\Users\us3r02\PycharmProjects\CNN_numbers_model\Pytorch_models\best_conv_net_model_X.pth", map_location=device))
model.eval()

def preprocess_roi(roi):
    import numpy as np
    MNIST_MEAN = 0.1307
    MNIST_STD = 0.3081

    if len(roi.shape) == 3: #случай RGB (BGR)
        roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    h,w = roi.shape[:2]
    # if h != 28 or w != 28:
    #     roi = cv2.resize(roi, (28, 28), interpolation=cv2.INTER_AREA)

    img = roi.copy()
    # pad = max(1, int(min(h, w) * 0.03))  # 3% от меньшей стороны
    # img = img[pad:h - pad, pad:w - pad] if (h > 2 * pad and w > 2 * pad) else img


    transform = transforms.Compose([
        transforms.ToTensor(),  # -> [1, 28, 28], значения [0..1]
        transforms.Normalize((0.1307,), (0.3081,))  # как у MNIST
    ])
    _, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # 4) Решаем инверсию: хотим, чтобы символ был white (255) на black (0)
    # Если среднее белое (фон светлый), то invert -> symbol bright
    if np.mean(thresh) > 127:
        bin_img = 255 - thresh
    else:
        bin_img = thresh

    # 5) Найдём bounding rect по ненулевым пикселям
    nz = cv2.findNonZero(bin_img)
    if nz is None:
        # пустой ROI — возьмём центральный crop и сделаем как есть
        center = cv2.resize(bin_img, (28, 28), interpolation=cv2.INTER_AREA)
        final = center
    else:
        x, y, bw, bh = cv2.boundingRect(nz)
        cut = bin_img[y:y + bh, x:x + bw]

        # 6) Вписываем в квадрат, центрируем
        size = max(bw, bh)
        square = np.zeros((size, size), dtype=np.uint8)
        y0 = (size - bh) // 2
        x0 = (size - bw) // 2
        square[y0:y0 + bh, x0:x0 + bw] = cut

        target_size = 20
        resized = cv2.resize(square, (target_size, target_size), interpolation=cv2.INTER_AREA)

        # создаём чёрный квадрат 28x28
        final = np.zeros((28, 28), dtype=np.uint8)

        # вставляем уменьшенную цифру в центр
        x_offset = (28 - target_size) // 2
        y_offset = (28 - target_size) // 2
        final[y_offset:y_offset + target_size, x_offset:x_offset + target_size] = resized

    # 7) Нормализация в float32 0..1
    arr = final.astype(np.float32) / 255.0

    # 8) Стандартизация как MNIST
    arr = (arr - MNIST_MEAN) / MNIST_STD
    cv2.imshow("sdff", bin_img)
    cv2.waitKey(0)
    # 9) to torch tensor, shape [1,1,28,28]
    tensor = torch.from_numpy(arr).unsqueeze(0).unsqueeze(0).type(torch.float32)

    return tensor

def predict_symbol(roi, model = model, divice = device, classes=None):
    model.eval()
    tensor = preprocess_roi(roi).to(divice)

    with torch.no_grad():
        out = model(tensor)
        probs = torch.softmax(out, dim=1).cpu().numpy().squeeze()
        idx = int(probs.argmax())
        conf = float(probs[idx])

    if classes:
        return classes[idx]
    else:
        return idx