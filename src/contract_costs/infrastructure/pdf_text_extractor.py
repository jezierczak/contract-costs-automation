import logging
import re
import cv2
import numpy as np
import pdfplumber
import pytesseract
from pathlib import Path
from pdf2image import convert_from_path
from PIL.Image import Image


class PdfTextExtractor:
    def extract(self, pdf_path: Path) -> str:
        text = self._extract_with_pdfplumber(pdf_path)
        if text.strip():
            return text

        logging.info("Fallback to OCR (tesseract)")
        images = convert_from_path(pdf_path)
        return self._extract_with_ocr(images[0])

    @staticmethod
    def _extract_with_pdfplumber(pdf_path: Path) -> str:
        text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    t = page.extract_text()
                    if t:
                        text += t + "\n"
        except Exception:
            logging.exception("pdfplumber failed")
        return text

    @staticmethod
    def _extract_with_ocr(image: Image) -> str:
        gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
        thresh = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )

        text = pytesseract.image_to_string(thresh, lang="pol")
        return re.sub(r"\n+", "\n", text).strip()
