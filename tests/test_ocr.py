from pathlib import Path
import tempfile
import unittest

import numpy as np

from CORE.scan_docs import crop_roi, CNNOCR, load_image


class OCRBoundaryTests(unittest.TestCase):
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
