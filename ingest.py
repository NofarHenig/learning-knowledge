import os

from dotenv import load_dotenv

from ingestion.udemy_source import UdemySource
from rag.chunker import chunk_document
from rag.openai_embedder import OpenAIEmbedder
from rag.postgres_vector_store import PostgresVectorStore


BATCH_SIZE = 50


load_dotenv()

connection_string = os.getenv("POSTGRES_CONNECTION_STRING")

if not connection_string:
    raise ValueError(
        "POSTGRES_CONNECTION_STRING is not configured"
    )

embedder = OpenAIEmbedder()

vector_store = PostgresVectorStore(
    connection_string=connection_string
)

source = UdemySource(
    lectures_file="data/lectures.json",
    captions_file="data/lecture_captions.json"
)

documents = source.load()

chunks = []

for document in documents:
    document_chunks = chunk_document(document)
    chunks.extend(document_chunks)

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

print(f"Indexed {len(chunks)} chunks")