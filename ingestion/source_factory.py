from pathlib import Path

from .directory_source import DirectorySource
from .pdf_source import PDFSource
from .text_source import TextSource
from .udemy_source import UdemySource


def create_source(
    source: str,
    collection: str
):
    if source == "udemy":
        return UdemySource(
            lectures_file="data/lectures.json",
            captions_file="data/lecture_captions.json",
            collection=collection
        )

    path = Path(source)

    if path.is_dir():
        return DirectorySource(
            directory_path=source,
            collection=collection
        )

    if path.suffix.lower() == ".pdf":
        return PDFSource(
            file_path=source,
            collection=collection
        )

    if path.suffix.lower() == ".txt":
        return TextSource(
            file_path=source,
            collection=collection
        )

    raise ValueError(
        f"Unsupported source: {source}"
    )