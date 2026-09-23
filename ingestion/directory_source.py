from pathlib import Path

from .source import Document


class DirectorySource:
    def __init__(
        self,
        directory_path: str,
        collection: str
    ):
        self.directory_path = Path(directory_path)
        self.collection = collection

    def load(self) -> list[Document]:
        documents = []

        for file_path in self.directory_path.glob("*.txt"):
            text = file_path.read_text(
                encoding="utf-8"
            )

            documents.append(
                Document(
                    text=text,
                    metadata={
                        "source": str(file_path),
                        "type": "text",
                        "collection": self.collection,
                        "title": file_path.stem
                    }
                )
            )

        return documents