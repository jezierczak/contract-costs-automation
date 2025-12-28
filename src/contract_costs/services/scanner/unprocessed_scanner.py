from pathlib import Path

def scan_unprocessed(folder: Path) -> list[Path]:
    return list(folder.glob("*.pdf"))