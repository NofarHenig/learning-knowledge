from pathlib import Path
from .source import Document

class TextSource:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)

    def load(self) -> list[Document]:
        text = self.file_path.read_text(encoding="utf-8")

        return [
            Document(
                text=text,
                metadata={
                    "source": str(self.file_path),
                    "type": "text"
                }
            )
        ]