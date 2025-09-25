import cv2
import matplotlib.pyplot as plt
import torch
from torchvision import datasets, transforms
from numsAndX import preprocess_roi

# ==== MNIST пример из train ====
trans = transforms.Compose([transforms.ToTensor(),
                            transforms.Normalize((0.1307,), (0.3081,))])
mnist_train = datasets.MNIST(root=r"C:\Users\us3r02\PycharmProjects\CNN_numbers_model\MNISTData",
                             train=True, download=True, transform=trans)

img_mnist, label_mnist = mnist_train[6]  # возьмём первую цифру
img_mnist_np = img_mnist.squeeze(0).numpy()

# ==== ROI из скана ====
roi_path = r"C:\Users\us3r02\PycharmProjects\ege_doc_scan\nums\1\1_3.jpg"
roi = cv2.imread(roi_path, cv2.IMREAD_GRAYSCALE)
tensor_roi = preprocess_roi(roi)
img_roi_np = tensor_roi.squeeze(0).squeeze(0).numpy()

# ==== Визуализация ====
plt.figure(figsize=(8,4))

plt.subplot(1,2,1)
plt.imshow(img_mnist_np, cmap="gray")
plt.title(f"MNIST train (label {label_mnist})")

plt.subplot(1,2,2)
plt.imshow(img_roi_np, cmap="gray")
plt.title("Your ROI after preprocess")

plt.show()

#print("Debug info for ROI:", debug_info)
