import cv2
from numsAndX import predict_symbol

classes = ['0', '1', '2', '3', '4', 'x']
for j in range(1, 5):
    for i in range(1, 5):
        pic_path = fr"C:\Users\us3r02\PycharmProjects\ege_doc_scan\nums\1\{j}_{i}.jpg"
        # загружаем ROI (например, обрезанный крестик или цифра)
        roi = cv2.imread(pic_path, cv2.IMREAD_GRAYSCALE)
        symbol = predict_symbol( roi, divice="cpu", classes=classes)
        print("Предсказанный символ:", symbol)