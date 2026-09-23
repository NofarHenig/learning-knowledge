from typing import Protocol
from ingestion.source import Document

class VectorStore(Protocol):
    def add(
        self,
        documents: list[Document],
        embeddings: list[list[float]]
    ) -> None:
        ...

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 3
    ) -> list[Document]:
        ...