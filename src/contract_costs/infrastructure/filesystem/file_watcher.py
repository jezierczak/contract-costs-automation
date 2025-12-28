from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class _Handler(FileSystemEventHandler):
    def __init__(self, on_file_created):
        self._on_file_created = on_file_created

    def on_created(self, event):
        if event.is_directory:
            return
        path = Path(event.src_path)
        if path.suffix.lower() != ".pdf":
            return
        self._on_file_created(path)


class FileWatcher:
    def __init__(self, path: Path, on_file_created) -> None:
        self._path = path
        self._on_file_created = on_file_created
        self._observer = Observer()

    def start(self) -> None:
        handler = _Handler(self._on_file_created)
        self._observer.schedule(handler, str(self._path), recursive=False)
        self._observer.start()

    def stop(self) -> None:
        self._observer.stop()
        self._observer.join()
