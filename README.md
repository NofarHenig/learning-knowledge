# Learning Material RAG

A reusable Retrieval-Augmented Generation (RAG) system for asking questions about indexed learning materials.

The system ingests learning content, converts it into searchable vector embeddings, retrieves the most relevant material for a question, and generates grounded answers with sources.

It supports multiple independent knowledge collections and exposes the RAG pipeline through an MCP server so AI clients and agents can use it as a tool.

## Architecture

```text
Learning Material
PDF / TXT / Directory
        |
        v
Source Adapter
        |
        v
Normalized Documents
        |
        v
Chunking
        |
        v
OpenAI Embeddings
        |
        v
PostgreSQL + pgvector
        |
        |  indexed by collection
        v
--------------------------------
        |
        | Query
        v
MCP Client / AI Agent
        |
        v
ask_knowledge(question, collection)
        |
        v
MCP Server
        |
        v
RAG Pipeline
        |
        +-------------------+
        |                   |
        v                   v
   Vector Search          LLM
        |                   |
        +---------> Context-+
                            |
                            v
                   Grounded Answer
                     + Sources
```

## How It Works

### 1. Ingestion

Learning material is loaded through a source adapter and normalized into a common `Document` representation.

Currently supported sources:

- PDF files
- Text files
- Directories containing text files

The source architecture is extensible, so additional content providers can be added without changing the shared RAG pipeline.

### 2. Chunking

Documents are split into smaller chunks before indexing.

Each chunk preserves metadata from its original document, including information such as:

- Source
- Collection
- Title
- Page number when available
- Chunk index

### 3. Embeddings

Each chunk is converted into a vector embedding using OpenAI embeddings.

The current implementation uses:

`text-embedding-3-small`

### 4. Vector Storage

Embeddings and document metadata are stored in PostgreSQL using the `pgvector` extension.

Each chunk receives a deterministic ID and is written using an UPSERT, making ingestion idempotent.

### 5. Retrieval

When a question is asked:

1. The question is converted into an embedding.
2. pgvector performs semantic similarity search.
3. Retrieval is restricted to the requested knowledge collection.
4. The most relevant chunks are returned.

This prevents unrelated collections from being mixed during retrieval.

### 6. Generation

The retrieved chunks are passed to the language model as context.

The model is instructed to answer using only the retrieved material and to state when the available context is insufficient.

The result contains:

- The generated answer
- The retrieved sources

## Knowledge Collections

The system supports multiple independent knowledge bases using collections.

For example:

```text
python-course
aws-course
system-design
company-training
```

A query is always scoped to a collection:

```text
ask_knowledge(
    question="How do I reverse a string in Python?",
    collection="python-course"
)
```

This allows the same RAG infrastructure to serve many independent sets of learning material.

## MCP Integration

The RAG pipeline is exposed through Model Context Protocol (MCP).

The server provides the tool:

```text
ask_knowledge(question, collection)
```

This separates the RAG implementation from the AI client using it.

Any compatible MCP client can interact with the knowledge base without needing to know how ingestion, embeddings, retrieval, or generation are implemented internally.

The MCP server supports:

- Local `stdio` transport
- Remote Streamable HTTP transport
- Bearer authentication for remote access

## Authentication

Remote MCP access is protected using Bearer authentication.

Requests without a valid access token are rejected before the MCP tool is executed.

The access token is provided to the application through environment configuration and is not stored in the repository.

In the AWS deployment, the token is stored in AWS Secrets Manager and injected into the ECS container at runtime.

This keeps authentication credentials separate from the application code and Docker image.

## Technology Stack

### Application

- Python
- OpenAI API
- MCP
- Docker

### RAG

- OpenAI embeddings
- PostgreSQL
- pgvector

### AWS

- Amazon ECS Fargate
- Amazon ECR
- Amazon Aurora PostgreSQL
- pgvector
- AWS IAM
- AWS Secrets Manager
- Amazon CloudWatch
- boto3

## AWS Deployment

The system has been containerized and deployed to AWS.

The cloud architecture uses:

```text
MCP Client
     |
     | Bearer Authentication
     v
Amazon ECS Fargate
     |
     | IAM Database Authentication
     v
Amazon Aurora PostgreSQL
     |
     v
pgvector
```

The Docker image is stored in Amazon ECR.

The application runs as an ECS Fargate task and connects to Aurora PostgreSQL using IAM database authentication rather than a stored database password.

Sensitive values such as the OpenAI API key and MCP access token are stored in AWS Secrets Manager and injected into the container at runtime.

CloudWatch is used for container logging.

The complete cloud flow has been tested end-to-end:

```text
Authenticated MCP Request
        |
        v
ECS Fargate
        |
        v
ask_knowledge
        |
        v
Question Embedding
        |
        v
Aurora PostgreSQL + pgvector
        |
        v
Relevant Learning Material
        |
        v
LLM Generation
        |
        v
Grounded Answer + Sources
```

Remote MCP authentication was also verified by confirming that unauthenticated requests are rejected while authenticated MCP requests are accepted.

## Database Authentication

The AWS deployment uses IAM authentication for Aurora PostgreSQL.

Instead of storing a database password, the application generates a temporary authentication token using `boto3`.

The ECS task role is granted permission to connect to the database through IAM.

This reduces the need for long-lived database credentials inside the application environment.

## Local Development

### Requirements

- Docker
- Docker Compose
- OpenAI API key

### Environment

Create a `.env` file based on `.env.example`.

Example:

```text
OPENAI_API_KEY=your_openai_api_key_here
POSTGRES_CONNECTION_STRING=postgresql://raguser:ragpassword@localhost:5432/learning_knowledge
KNOWLEDGE_COLLECTION=example-collection
KNOWLEDGE_SOURCE=materials/example.pdf
```

Never commit the real `.env` file.

### Start PostgreSQL

```bash
docker compose up -d postgres
```

### Ingest Learning Material

Configure:

```text
KNOWLEDGE_COLLECTION=example-collection
KNOWLEDGE_SOURCE=materials/example.pdf
```

Then run:

```bash
docker compose run --rm ingest
```

The ingestion pipeline:

1. Loads the source.
2. Normalizes it into documents.
3. Splits documents into chunks.
4. Generates embeddings.
5. Stores the chunks and vectors in PostgreSQL.

### Ask a Question

```bash
docker compose run --rm app
```

The application retrieves relevant chunks from the configured collection and generates a grounded answer.

## Running the MCP Server

### Local stdio

```bash
python -m mcp_server.server
```

### Streamable HTTP

Set:

```text
MCP_TRANSPORT=streamable-http
MCP_ACCESS_TOKEN=your_secure_token
MCP_RESOURCE_URL=http://localhost:8000/mcp
```

Then run:

```bash
python -m mcp_server.server
```

The MCP endpoint is available at:

```text
http://localhost:8000/mcp
```

Remote HTTP access requires a valid Bearer token.

## Project Structure

```text
learning-knowledge/
├── db/
│   └── init.sql
├── ingestion/
│   ├── source.py
│   ├── source_factory.py
│   ├── text_source.py
│   ├── directory_source.py
│   └── pdf_source.py
├── materials/
├── mcp_client/
│   └── client.py
├── mcp_server/
│   └── server.py
├── rag/
│   ├── chunker.py
│   ├── database_connection.py
│   ├── embedder.py
│   ├── generator.py
│   ├── openai_embedder.py
│   ├── openai_generator.py
│   ├── postgres_vector_store.py
│   ├── rag_pipeline.py
│   └── vector_store.py
├── ask.py
├── ingest.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── SKILL.md
└── README.md
```

## Design Decisions

### Source-Agnostic Ingestion

All content sources are normalized into the same `Document` model.

The RAG pipeline therefore does not depend on where the learning material originated.

### Dependency Inversion

The RAG pipeline depends on abstractions for:

- Embeddings
- Vector storage
- Generation

This keeps the core pipeline independent from specific providers.

### Collection Isolation

Every query specifies a collection.

Retrieval filters by collection before selecting the most relevant chunks.

### Idempotent Ingestion

Chunk IDs are generated deterministically.

Re-ingesting the same content updates the existing records instead of creating duplicates.

### Separate Indexing and Query Paths

Ingestion is an offline/update operation.

Question answering is an online retrieval and generation operation.

This keeps expensive document processing out of the request path.

### MCP as an Integration Layer

MCP is not required for the RAG pipeline itself.

It is used as an integration layer so external AI clients and agents can access the RAG system through a standard tool interface.

### Secrets Outside the Application

Production secrets are not stored in source control or inside the Docker image.

AWS Secrets Manager provides sensitive application credentials at runtime.

## Skill

The repository also contains an Agent Skill:

`learning-material-rag`

The Skill instructs compatible AI agents how to use the `ask_knowledge` MCP tool to query indexed learning material.

The Skill and MCP server serve different purposes:

```text
Skill
  |
  | tells the agent when and how
  | to use the capability
  v
MCP Tool
  |
  | provides the actual capability
  v
RAG Pipeline
```

Installing the Skill does not automatically provide access to a hosted MCP server. The MCP server must be configured separately by the client.

## Current Limitations

- Chunking is currently sentence/character based rather than token-aware.
- Chunks do not currently overlap.
- Retrieval uses vector similarity without a reranking stage.
- Vector dimensions are currently tied to the selected embedding model.
- Directory ingestion currently supports text files.
- PDF ingestion expects extractable text and does not perform OCR.
- Source reporting is basic rather than full inline citation generation.
- Remote authentication currently uses a static Bearer token rather than per-user OAuth.
- A stable always-on public MCP endpoint is not currently provided.

## Future Improvements

Potential improvements include:

- Token-aware recursive chunking
- Chunk overlap
- Hybrid vector and keyword retrieval
- Reranking
- Retrieval evaluation and golden datasets
- Incremental indexing
- HNSW or IVFFlat indexes for larger datasets
- Additional learning-source adapters
- Additional embedding and generation providers
- Improved source citations
- Per-user authentication
- OAuth support
- Rate limiting
- Stable production MCP endpoint

## Security

Do not commit:

- `.env`
- API keys
- MCP access tokens
- AWS credentials
- Database credentials
- Private or copyrighted learning material

The repository is intended to contain the RAG infrastructure and integration code, not private learning content or credentials.

## License

Add the appropriate license for your intended use.