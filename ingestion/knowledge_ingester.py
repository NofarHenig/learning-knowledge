from ingestion.source import Document
from rag.chunker import chunk_document


BATCH_SIZE = 50


class KnowledgeIngester:
    def __init__(
        self,
        embedder,
        vector_store
    ):
        self.embedder = embedder
        self.vector_store = vector_store

    def ingest_text(
        self,
        text: str,
        filename: str,
        collection: str
    ) -> int:
        document = Document(
            text=text,
            metadata={
                "title": filename,
                "source": filename,
                "collection": collection
            }
        )

        chunks = chunk_document(document)

        for start_index in range(
            0,
            len(chunks),
            BATCH_SIZE
        ):
            batch = chunks[
                start_index:
                start_index + BATCH_SIZE
            ]

            texts = [
                chunk.text
                for chunk in batch
            ]

            embeddings = self.embedder.embed(
                texts
            )

            self.vector_store.add(
                documents=batch,
                embeddings=embeddings
            )

        return len(chunks)