from pathlib import Path

from girbridge.adapters.storage import FileStorage


def test_write_and_read_text(tmp_path: Path) -> None:
    storage = FileStorage()
    target = tmp_path / "nested" / "sample.txt"

    storage.write_text(target, "hello")

    assert target.exists()
    assert storage.read_text(target) == "hello"


def test_copy_file_creates_parent_and_copies_content(tmp_path: Path) -> None:
    storage = FileStorage()
    source = tmp_path / "source.txt"
    destination = tmp_path / "deep" / "target.txt"
    source.write_text("content", encoding="utf-8")

    storage.copy_file(source, destination)

    assert destination.exists()
    assert destination.read_text(encoding="utf-8") == "content"
