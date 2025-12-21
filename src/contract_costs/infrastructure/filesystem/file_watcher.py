from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time


class _Handler(FileSystemEventHandler):
    def __init__(self, on_file_created):
        self._on_file_created = on_file_created

    def on_created(self, event):
        if event.is_directory:
            return
        self._on_file_created(Path(event.src_path))


class FileWatcher:
    def __init__(self, path: Path, on_file_created) -> None:
        self._path = path
        self._on_file_created = on_file_created
        self._observer = Observer()

    def start(self) -> None:
        handler = _Handler(self._on_file_created)
        self._observer.schedule(handler, str(self._path), recursive=False)
        self._observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self) -> None:
        self._observer.stop()
        self._observer.join()
