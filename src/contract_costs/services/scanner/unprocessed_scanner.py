from pathlib import Path

def scan_unprocessed(folder: Path) -> list[Path]:
    pdfs = folder.glob("*.pdf")
    xmls = folder.glob("*.xml")
    return list(pdfs) + list(xmls)