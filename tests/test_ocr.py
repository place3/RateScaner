from pathlib import Path
import json
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from CORE.scan_docs import crop_roi, CNNOCR, load_image
from scaner_service import run_scan


class OCRBoundaryTests(unittest.TestCase):
    def test_recognition_is_saved_when_expert_id_needs_correction(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            inputs = root / "input"
            inputs.mkdir()
            (inputs / "page.jpg").write_bytes(b"placeholder; image reader is mocked")
            page = {"expert_id": "", "works": {"001": [1, 2, 0, "X", 0, 1]}}
            with patch("CORE.scan_docs.CNNOCR"), patch("CORE.scan_docs.ImgScanner") as scanner:
                scanner.return_value.get_structure_data.return_value = page
                with self.assertRaisesRegex(ValueError, "Data saved"):
                    run_scan(scans_root=inputs, res_path=root / "review", model_path="mocked.pth")
            saved = json.loads((root / "review/recognized_pages.json").read_text())
            self.assertEqual(saved, [page])
            self.assertFalse((root / "review/results.xlsx").exists())

    def test_crop_bounds_are_validated(self):
        image = np.zeros((100, 100), dtype=np.uint8)
        self.assertEqual(crop_roi(image, [0, 0, 30, 30]).shape, (18, 18))
        for region in ([90, 90, 30, 30], [-1, 0, 30, 30], [0, 0, 10, 10]):
            with self.subTest(region=region), self.assertRaises(ValueError):
                crop_roi(image, region)

    def test_missing_checkpoint_does_not_use_random_weights(self):
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(FileNotFoundError, "Model weights not found"):
                CNNOCR(Path(temporary) / "missing.pth")

    def test_empty_or_invalid_image_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "bad.png"
            for data in (b"", b"not an image"):
                path.write_bytes(data)
                with self.subTest(data=data), self.assertRaises(ValueError):
                    load_image(path)


if __name__ == "__main__":
    unittest.main()
