from pathlib import Path

from .source import Document


class TextSource:
    def __init__(
        self,
        file_path: str,
        collection: str
    ):
        self.file_path = Path(file_path)
        self.collection = collection

    def load(self) -> list[Document]:
        text = self.file_path.read_text(
            encoding="utf-8"
        )

        return [
            Document(
                text=text,
                metadata={
                    "source": str(self.file_path),
                    "type": "text",
                    "collection": self.collection,
                    "title": self.file_path.stem
                }
            )
        ]