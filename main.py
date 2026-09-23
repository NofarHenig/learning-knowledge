import os

from dotenv import load_dotenv

from ingestion.udemy_source import UdemySource
from rag.chunker import chunk_document
from rag.openai_embedder import OpenAIEmbedder
from rag.openai_generator import OpenAIGenerator
from rag.postgres_vector_store import PostgresVectorStore
from rag.rag_pipeline import RagPipeline


load_dotenv()

connection_string = os.getenv("POSTGRES_CONNECTION_STRING")

if not connection_string:
    raise ValueError(
        "POSTGRES_CONNECTION_STRING is not configured"
    )


# Build the dependencies

embedder = OpenAIEmbedder()

vector_store = PostgresVectorStore(
    connection_string=connection_string
)

generator = OpenAIGenerator()


# Ingestion

source = UdemySource(
    lectures_file="data/lectures.json",
    captions_file="data/lecture_captions.json",
    limit=1
)

documents = source.load()

chunks = []

for document in documents:
    document_chunks = chunk_document(document)
    chunks.extend(document_chunks)

texts = []

for chunk in chunks:
    texts.append(chunk.text)

embeddings = embedder.embed(texts)

vector_store.add(
    documents=chunks,
    embeddings=embeddings
)

print(f"Stored {len(chunks)} chunks in PostgreSQL")


# RAG

rag = RagPipeline(
    embedder=embedder,
    vector_store=vector_store,
    generator=generator
)

question = "What should I do if I get stuck while learning Python?"

answer = rag.ask(question)

print("\nQuestion:")
print(question)

print("\nAnswer:")
print(answer)