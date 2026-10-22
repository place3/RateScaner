"""Architecture shared by inference; layer names match the training checkpoint."""

from pathlib import Path

import torch
from torch import nn


CLASS_MAP = ("0", "1", "2", "3", "4", "X")


class ConvNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.layer1 = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=5, stride=1, padding=2),
            nn.ReLU(), nn.MaxPool2d(2, 2),
        )
        self.layer2 = nn.Sequential(
            nn.Conv2d(32, 64, kernel_size=5, stride=1, padding=2),
            nn.ReLU(), nn.MaxPool2d(2, 2),
        )
        self.drop_out = nn.Dropout()
        self.fc1 = nn.Linear(7 * 7 * 64, 1000)
        self.fc2 = nn.Linear(1000, len(CLASS_MAP))

    def forward(self, x):
        x = self.layer2(self.layer1(x))
        return self.fc2(self.fc1(self.drop_out(x.reshape(x.size(0), -1))))


def load_model(path):
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Model weights not found: {path}. See README.md.")
    # CPU inference is sufficient for this small model and works without CUDA.
    model = ConvNet()
    model.load_state_dict(torch.load(path, map_location="cpu", weights_only=True))
    model.eval()
    return model
