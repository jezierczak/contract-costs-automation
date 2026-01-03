import logging
import re


import cv2
import numpy as np

import pytesseract #typed: ignore
from pathlib import Path
from pdf2image import convert_from_path
from PIL import Image
from multiprocessing import Process, Queue
import pdfplumber


logger = logging.getLogger(__name__)

custom_config = r"""
--oem 3
--psm 6
-c preserve_interword_spaces=1
"""

class PdfTextExtractor:
    def extract(self, pdf_path: Path) -> str:
        text = self.extract_with_pdfplumber_safe(pdf_path, timeout=5)
        if text.strip():
            logger.info("PDF extractor used pdfplumber")
            return text

        logger.info("Fallback to OCR (tesseract)")
        images = convert_from_path(     pdf_path,
                                        dpi=300,          # MINIMUM
                                        fmt="png",
                                        grayscale=True)

        texts = []

        for i, img in enumerate(images, start=1):
            page_text = self._extract_with_ocr(img)
            if page_text:
                texts.append(
                    f"\n=== PAGE {i} ===\n{page_text}"
                )

        return "\n".join(texts)

    @staticmethod
    def _extract_with_pdfplumber(pdf_path: Path) -> str:
        text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages, start=1):
                    logging.info("pdfplumber: extracting page %d", i)
                    t = page.extract_text()
                    logging.info("pdfplumber: page %d extracted", i)

                    if t:
                        text += t + "\n"
        except Exception:
            logging.exception("pdfplumber failed")
        return text
    @staticmethod
    def extract_with_pdfplumber_safe(pdf_path: Path, timeout: int = 5) -> str:
        q: Queue = Queue()
        p = Process(target=PdfTextExtractor._pdfplumber_worker, args=(pdf_path, q))
        p.start()
        p.join(timeout)

        if p.is_alive():
            logger.warning("pdfplumber timeout, killing process")
            p.terminate()
            p.join()
            return ""

        try:
            return q.get_nowait()
        except Exception:
            return ""



    @staticmethod
    def _extract_with_ocr(image: Image.Image) -> str:
        try:
            gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
            #odszumianie
            gray = cv2.fastNlMeansDenoising(gray, h=30)

            # podbicie kontrastu (CLAHE)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            gray = clahe.apply(gray)

            # thresh = cv2.adaptiveThreshold(
            #     gray, 255,
            #     cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            #     cv2.THRESH_BINARY, 11, 2
            # )

            _,thresh = cv2.threshold(
                gray, 0, 255,
                cv2.THRESH_BINARY + cv2.THRESH_OTSU
            )

            # thresh = Image.fromarray(thresh)
            # text = pytesseract.image_to_string(thresh, lang="pol")

            text = pytesseract.image_to_string(
                thresh,
                lang="pol",
                config=custom_config
            )

            if text is None:
                logger.warning("OCR returned None")
                return ""

            text = text.strip()
            if not text:
                logger.warning("OCR returned empty text")
                return ""

            # result = PdfTextExtractor._split_companies_by_nip(text)

            return re.sub(r"\n+", "\n", text)

        except Exception:
            logger.exception("OCR failed completely")
            return ""
    @staticmethod
    def _split_companies_by_nip(text: str) -> str:
        nips = re.findall(r"\b\d{10}\b", text)
        if len(nips) >= 2:
            # rozbij tekst na części wokół NIP-ów
            parts = re.split(r"\b\d{10}\b", text)
            return (
                    "=== COMPANY LEFT ===\n"
                    + parts[0] + nips[0] +
                    "\n=== COMPANY RIGHT ===\n"
                    + parts[1] + nips[1]
            )
        return text

    # @staticmethod
    # def _pdfplumber_worker(pdf_path: Path, q: Queue):
    #     try:
    #         text = ""
    #         with pdfplumber.open(pdf_path) as pdf:
    #             for page in pdf.pages[:3]:  # max 3 strony
    #                 t = page.extract_text()
    #                 if t:
    #                     text += t + "\n"
    #         q.put(text)
    #     except Exception:
    #         q.put("")

    @staticmethod
    def _pdfplumber_worker(pdf_path: Path, q: Queue):
        try:
            text_parts: list[str] = []

            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages[:3]:  # max 3 strony
                    full_text = page.extract_text()

                    # ❌ brak pełnego tekstu → NIE jest sukces pdfplumber
                    if not full_text or not full_text.strip():
                        continue

                    page_height = page.height
                    page_width = page.width
                    mid_x = page_width / 2
                    header_limit = page_height * 0.35

                    words = page.extract_words(
                        use_text_flow=False,
                        x_tolerance=2,
                        y_tolerance=3,
                    )

                    left, right = [], []

                    for w in words:
                        if w["top"] > header_limit:
                            continue
                        if w["x0"] < mid_x:
                            left.append(w)
                        else:
                            right.append(w)

                    def join_words(wordss):
                        lines = {}
                        for ww in wordss:
                            key = round(ww["top"], 1)
                            lines.setdefault(key, []).append(ww["text"])
                        return "\n".join(
                            " ".join(v) for _, v in sorted(lines.items())
                        )

                    left_text = join_words(left)
                    right_text = join_words(right)

                    header_text = ""
                    if left_text or right_text:
                        header_text = (
                                "=== HEADER (COLUMNS) ===\n"
                                "LEFT:\n"
                                + left_text
                                + "\n\nRIGHT:\n"
                                + right_text
                                + "\n"
                        )

                    page_text = (
                            header_text
                            + "\n=== FULL DOCUMENT TEXT ===\n"
                            + full_text
                    )

                    text_parts.append(page_text)

            # ❌ jeśli NIE udało się wydobyć pełnego tekstu z żadnej strony
            if not text_parts:
                q.put("")
            else:
                q.put("\n\n".join(text_parts))

        except Exception:
            q.put("")

