from pathlib import Path
from .text_source import TextSource
from .directory_source import DirectorySource
from .udemy_source import UdemySource

def create_source(source: str):
    if source == "udemy":
        return UdemySource(
            lectures_file="data/lectures.json",
            captions_file="data/lecture_captions.json"
        )

    if source.startswith("http://") or source.startswith("https://"):
        return "url"

    path = Path(source)

    if path.is_dir():
        return DirectorySource(source)

    if path.suffix.lower() == ".pdf":
        return "pdf"

    if path.suffix.lower() == ".txt":
        return TextSource(source)

    raise ValueError(f"Unsupported source: {source}")