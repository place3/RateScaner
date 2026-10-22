"""Command-line entry point for OCR or export of manually verified recognition data."""

import argparse
import json
from pathlib import Path
import sys

from scanner_pipeline import process_pages

ROOT = Path(__file__).resolve().parent
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}


def run_scan(n_pages=None, scans_root="", res_path="", *, model_path=None,
             rois_path=ROOT / "data/ROIs.json", work_count=6):
    directory = Path(scans_root)
    if not directory.is_dir():
        raise ValueError(f"Input directory not found: {directory}")
    images = sorted(path for path in directory.iterdir()
                    if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES)
    if not images:
        raise ValueError("No supported images in input directory")
    if n_pages is not None and len(images) != n_pages:
        raise ValueError(f"Expected {n_pages} images, found {len(images)}")
    if model_path is None:
        raise ValueError("Specify model_path or --model. See README.md.")
    if Path(res_path).exists():
        raise FileExistsError(f"Output directory already exists: {res_path}. Choose a new directory.")
    from CORE.scan_docs import CNNOCR, ImgScanner
    ocr = CNNOCR(model_path)
    pages = []
    for image in images:
        try:
            page = ImgScanner(image, ocr, rois_path, work_count).get_structure_data()
        except (ValueError, KeyError) as error:
            raise ValueError(f"{image.name}: {error}") from error
        pages.append(page)
    return str(process_pages(pages, res_path))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Compare two experts' protocol scores; export SQLite and Excel.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", type=Path, help="Directory containing only the protocol images to process")
    source.add_argument("--from-json", type=Path, help="Manually verified recognized pages; bypass OCR")
    parser.add_argument("--output", required=True, type=Path, help="New output directory (must not already exist)")
    parser.add_argument("--model", type=Path, help="Trusted best_conv_net_model_X.pth checkpoint")
    parser.add_argument("--rois", type=Path, default=ROOT / "data/ROIs.json")
    parser.add_argument("--work-count", type=int, choices=range(1, 11), default=6)
    parser.add_argument("--tesseract", help="Optional path to the Tesseract executable")
    args = parser.parse_args(argv)
    try:
        if args.from_json:
            pages = json.loads(args.from_json.read_text(encoding="utf-8"))
            result = process_pages(pages, args.output)
        else:
            if not args.model:
                parser.error("--model is required with --input")
            if args.tesseract:
                import pytesseract
                pytesseract.pytesseract.tesseract_cmd = args.tesseract
            result = run_scan(scans_root=args.input, res_path=args.output, model_path=args.model,
                              rois_path=args.rois, work_count=args.work_count)
    except (OSError, ValueError, RuntimeError) as error:
        parser.exit(1, f"Error: {error}\n")
    print(f"Results saved to: {result}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
