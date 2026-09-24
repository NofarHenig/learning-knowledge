from dotenv import load_dotenv

from ingestion.source_factory import create_source
from rag.chunker import chunk_document
from rag.database_connection import get_postgres_connection_string
from rag.openai_embedder import OpenAIEmbedder
from rag.postgres_vector_store import PostgresVectorStore


BATCH_SIZE = 50


load_dotenv()

connection_string = get_postgres_connection_string()

import os

collection = os.getenv("KNOWLEDGE_COLLECTION")
source_path = os.getenv("KNOWLEDGE_SOURCE")

if not collection:
    raise ValueError(
        "KNOWLEDGE_COLLECTION is not configured"
    )

if not source_path:
    raise ValueError(
        "KNOWLEDGE_SOURCE is not configured"
    )

embedder = OpenAIEmbedder()

vector_store = PostgresVectorStore(
    connection_string=connection_string
)

source = create_source(
    source=source_path,
    collection=collection
)

documents = source.load()

chunks = []

for document in documents:
    document_chunks = chunk_document(document)
    chunks.extend(document_chunks)

print(f"Source: {source_path}")
print(f"Collection: {collection}")
print(f"Loaded {len(documents)} documents")
print(f"Created {len(chunks)} chunks")

for start_index in range(0, len(chunks), BATCH_SIZE):
    batch = chunks[
        start_index:start_index + BATCH_SIZE
    ]

    texts = []

    for chunk in batch:
        texts.append(chunk.text)

    embeddings = embedder.embed(texts)

    vector_store.add(
        documents=batch,
        embeddings=embeddings
    )

    print(
        f"Indexed batch "
        f"{start_index + 1}-"
        f"{start_index + len(batch)}"
    )

print(
    f"Indexed {len(chunks)} chunks "
    f"into collection '{collection}'"
)