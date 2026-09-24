import os
import secrets

from dotenv import load_dotenv
from mcp.server import MCPServer
from mcp.server.auth.provider import AccessToken, TokenVerifier
from mcp.server.auth.settings import AuthSettings
from pydantic import AnyHttpUrl

from ingestion.knowledge_ingester import KnowledgeIngester
from rag.database_connection import get_postgres_connection_string
from rag.openai_embedder import OpenAIEmbedder
from rag.openai_generator import OpenAIGenerator
from rag.postgres_vector_store import PostgresVectorStore
from rag.rag_pipeline import RagPipeline


load_dotenv()


class StaticTokenVerifier(TokenVerifier):
    def __init__(
        self,
        access_token: str,
        resource_url: str
    ):
        self.access_token = access_token
        self.resource_url = resource_url

    async def verify_token(
        self,
        token: str
    ) -> AccessToken | None:
        if not secrets.compare_digest(
            token,
            self.access_token
        ):
            return None

        return AccessToken(
            token=token,
            client_id="learning-knowledge-client",
            scopes=["knowledge:read"],
            resource=self.resource_url
        )


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

ingester = KnowledgeIngester(
    embedder=embedder,
    vector_store=vector_store
)


transport = os.getenv(
    "MCP_TRANSPORT",
    "stdio"
)

access_token = os.getenv("MCP_ACCESS_TOKEN")

resource_url = os.getenv(
    "MCP_RESOURCE_URL",
    "http://localhost:8000/mcp"
)


if transport == "streamable-http":
    if not access_token:
        raise ValueError(
            "MCP_ACCESS_TOKEN is required "
            "for streamable-http transport"
        )

    server = MCPServer(
        "learning-knowledge",
        token_verifier=StaticTokenVerifier(
            access_token=access_token,
            resource_url=resource_url
        ),
        auth=AuthSettings(
            issuer_url=AnyHttpUrl(
                "https://learning-knowledge.local"
            ),
            resource_server_url=AnyHttpUrl(
                resource_url
            ),
            required_scopes=[
                "knowledge:read"
            ],
            validate_token_resource=True
        )
    )
else:
    server = MCPServer(
        "learning-knowledge"
    )


@server.tool()
def add_knowledge(
    text: str,
    filename: str,
    collection: str
) -> str:
    """
    Add text content to a knowledge collection so it can
    later be queried through the RAG system.
    """
    if not text.strip():
        raise ValueError(
            "Text cannot be empty"
        )

    if not filename.strip():
        raise ValueError(
            "Filename cannot be empty"
        )

    if not collection.strip():
        raise ValueError(
            "Collection cannot be empty"
        )

    chunk_count = ingester.ingest_text(
        text=text,
        filename=filename,
        collection=collection
    )

    return (
        f"Added '{filename}' to collection "
        f"'{collection}' as {chunk_count} chunks."
    )


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