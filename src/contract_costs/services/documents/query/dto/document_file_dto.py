from dataclasses import dataclass


@dataclass(frozen=True,slots=True)
class DocumentFileDto:
    file_path: str
    ksef_number: str | None = None
