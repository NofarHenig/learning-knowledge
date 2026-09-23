from pathlib import Path
from pypdf import PdfReader
from .source import Document

class PDFSource:
    def __init__(
        self,
        file_path: str,
        collection: str
    ):
        self.file_path = Path(file_path)
        self.collection = collection

    def load(self) -> list[Document]:
        reader = PdfReader(self.file_path)

        documents = []

        for page_number, page in enumerate(
            reader.pages,
            start=1
        ):
            text = page.extract_text()

            if not text:
                continue

            documents.append(
                Document(
                    text=text,
                    metadata={
                        "source": str(self.file_path),
                        "type": "pdf",
                        "collection": self.collection,
                        "page": page_number,
                        "title": self.file_path.stem
                    }
                )
            )

        return documents