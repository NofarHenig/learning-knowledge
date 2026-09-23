from dataclasses import dataclass

from ingestion.source import Document
from rag.embedder import Embedder
from rag.generator import Generator
from rag.vector_store import VectorStore


@dataclass
class RagResult:
    answer: str
    sources: list[Document]


class RagPipeline:
    def __init__(
        self,
        embedder: Embedder,
        vector_store: VectorStore,
        generator: Generator
    ):
        self.embedder = embedder
        self.vector_store = vector_store
        self.generator = generator

    def ask(
        self,
        question: str,
        top_k: int = 3
    ) -> RagResult:
        question_embedding = self.embedder.embed([question])[0]

        documents = self.vector_store.search(
            query_embedding=question_embedding,
            top_k=top_k
        )

        context_parts = []

        for document in documents:
            context_parts.append(document.text)

        context = "\n\n".join(context_parts)

        answer = self.generator.generate(
            question=question,
            context=context
        )

        return RagResult(
            answer=answer,
            sources=documents
        )