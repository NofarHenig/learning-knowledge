import json

import psycopg
from pgvector.psycopg import register_vector

from ingestion.source import Document


class PostgresVectorStore:
    def __init__(self, connection_string: str):
        self.connection = psycopg.connect(connection_string)
        register_vector(self.connection)

    def add(
        self,
        documents: list[Document],
        embeddings: list[list[float]]
    ) -> None:
        if len(documents) != len(embeddings):
            raise ValueError(
                "The number of documents must match the number of embeddings"
            )

        with self.connection.cursor() as cursor:
            for document, embedding in zip(documents, embeddings):
                lecture_id = document.metadata["lecture_id"]
                chunk_index = document.metadata["chunk_index"]

                chunk_id = f"udemy_{lecture_id}_{chunk_index}"

                cursor.execute(
                    """
                    INSERT INTO chunks (id, text, metadata, embedding)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (id)
                    DO UPDATE SET
                        text = EXCLUDED.text,
                        metadata = EXCLUDED.metadata,
                        embedding = EXCLUDED.embedding
                    """,
                    (
                        chunk_id,
                        document.text,
                        json.dumps(document.metadata),
                        embedding
                    )
                )

        self.connection.commit()

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 3
    ) -> list[Document]:
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT text, metadata
                FROM chunks
                ORDER BY embedding <=> %s::vector
                LIMIT %s
                """,
                (
                    query_embedding,
                    top_k
                )
            )

            rows = cursor.fetchall()

        documents = []

        for text, metadata in rows:
            documents.append(
                Document(
                    text=text,
                    metadata=metadata
                )
            )

        return documents