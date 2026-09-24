import os

from dotenv import load_dotenv
from mcp.server import MCPServer

from rag.database_connection import get_postgres_connection_string
from rag.openai_embedder import OpenAIEmbedder
from rag.openai_generator import OpenAIGenerator
from rag.postgres_vector_store import PostgresVectorStore
from rag.rag_pipeline import RagPipeline


load_dotenv()

connection_string = get_postgres_connection_string()

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


server = MCPServer("learning-knowledge")


@server.tool()
def ask_knowledge(
    question: str,
    collection: str
) -> str:
    """
    Answer a question using material from the selected
    knowledge collection.
    """
    result = rag.ask(
        question=question,
        collection=collection
    )

    source_titles = []

    for document in result.sources:
        title = document.metadata.get(
            "title",
            "Unknown source"
        )

        if title not in source_titles:
            source_titles.append(title)

    sources_text = "\n".join(
        f"- {title}"
        for title in source_titles
    )

    return (
        f"{result.answer}\n\n"
        f"Sources:\n"
        f"{sources_text}"
    )


if __name__ == "__main__":
    transport = os.getenv(
        "MCP_TRANSPORT",
        "stdio"
    )

    if transport == "streamable-http":
        server.run(
            transport="streamable-http",
            host="0.0.0.0",
            port=8000,
            stateless_http=True,
            json_response=True
        )
    else:
        server.run(
            transport="stdio"
        )