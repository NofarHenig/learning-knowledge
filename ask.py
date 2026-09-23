import os

from dotenv import load_dotenv

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

embedder = OpenAIEmbedder()

vector_store = PostgresVectorStore(
    connection_string=connection_string
)

generator = OpenAIGenerator()

rag = RagPipeline(
    embedder=embedder,
    vector_store=vector_store,
    generator=generator
)

question = "Why should I learn Python?"

result = rag.ask(question)

print("\nQuestion:")
print(question)

print("\nAnswer:")
print(result.answer)

print("\nSources:")

source_titles = []

for document in result.sources:
    title = document.metadata.get(
        "title",
        "Unknown source"
    )

    if title not in source_titles:
        source_titles.append(title)

for title in source_titles:
    print(f"- {title}")