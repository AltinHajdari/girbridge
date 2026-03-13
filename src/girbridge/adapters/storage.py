import shutil
from pathlib import Path


class FileStorage:
    def read_text(self, path: Path) -> str:
        return path.read_text(encoding="utf-8")

    def write_text(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def copy_file(self, src: Path, dst: Path) -> None:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
