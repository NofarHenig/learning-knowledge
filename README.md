# Learning Knowledge RAG

A reusable Retrieval-Augmented Generation (RAG) system that turns learning material into a searchable knowledge base and exposes it to AI clients through MCP.

The project was initially built using Python course transcripts, but the architecture separates content ingestion from retrieval so additional sources can be supported.

## Architecture

```text
Learning Material
      |
      v
Content Source
      |
      v
Documents
      |
      v
Chunking
      |
      v
Embeddings
      |
      v
PostgreSQL + pgvector
      |
      v
Semantic Retrieval
      |
      v
LLM Generation
      |
      v
Answer + Sources
      |
      v
MCP Server
      |
      v
AI Client / Agent
```

## How It Works

### 1. Ingestion

Learning material is converted into a common `Document` representation containing text and metadata.

The current implementation supports Udemy course transcripts, while the ingestion layer is designed to support additional sources such as text files, PDFs, and other learning material.

### 2. Chunking

Documents are split into smaller chunks before indexing.

Each chunk keeps the metadata of its original document, allowing retrieved information to be traced back to its source.

### 3. Embeddings

Chunks are converted into vector embeddings using OpenAI embeddings.

The same embedding model is used to convert user questions into vectors.

### 4. Vector Search

Embeddings are stored in PostgreSQL using the pgvector extension.

When a question is asked, cosine distance is used to retrieve the most semantically relevant chunks.

### 5. RAG Generation

The retrieved chunks are provided to the LLM as context.

The model is instructed to answer using only the retrieved course material and to report when the available context is insufficient.

### 6. MCP

The RAG pipeline is exposed through a Model Context Protocol (MCP) server.

This keeps the retrieval implementation independent from a specific AI application and allows MCP-compatible clients or agents to use the knowledge base as a tool.

## Example

Question:

```text
How do I reverse a string in Python?
```

The system:

```text
Question
   ↓
Embedding
   ↓
Vector Search
   ↓
Top-K Course Chunks
   ↓
LLM
   ↓
Answer + Sources
```

Example retrieved sources:

```text
Methods and Functions Homework - Solutions
Methods and Functions Homework Overview
Function Practice - Solutions Level One
```

## Tech Stack

- Python
- OpenAI API
- PostgreSQL
- pgvector
- Docker / Docker Compose
- Model Context Protocol (MCP)

## Project Structure

```text
learning-knowledge/
├── ingestion/
│   ├── source.py
│   ├── ingest.py
│   ├── source_factory.py
│   ├── text_source.py
│   ├── directory_source.py
│   └── udemy_source.py
├── rag/
│   ├── chunker.py
│   ├── embedder.py
│   ├── generator.py
│   ├── openai_embedder.py
│   ├── openai_generator.py
│   ├── vector_store.py
│   ├── postgres_vector_store.py
│   └── rag_pipeline.py
├── mcp_server/
│   └── server.py
├── mcp_client/
│   └── client.py
├── db/
│   └── init.sql
├── ingest.py
├── ask.py
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## Configuration

Create a `.env` file based on `.env.example`:

```text
OPENAI_API_KEY=your_openai_api_key_here
POSTGRES_CONNECTION_STRING=postgresql://raguser:ragpassword@localhost:5432/learning_knowledge
```

Never commit the real `.env` file or API keys.

## Running the Project

Start PostgreSQL:

```bash
docker compose up -d postgres
```

Build and run the ingestion pipeline:

```bash
docker compose build ingest
docker compose run --rm ingest
```

Run the MCP client:

```bash
python -m mcp_client.client
```

Then enter a question about the indexed learning material.

## Design Decisions

The project uses abstractions for `Embedder`, `VectorStore`, and `Generator`, keeping the core RAG pipeline independent from specific infrastructure providers.

Indexing and querying are separate flows. Ingestion can therefore happen offline, while questions can be served against the already indexed knowledge base.

Chunk IDs are deterministic and PostgreSQL uses UPSERT operations, making repeated indexing idempotent.

Embedding requests are processed in batches to support larger knowledge bases efficiently.

## Future Improvements

- Additional content loaders such as PDF and YouTube
- Local caching of source transcripts
- Token-aware chunking and chunk overlap
- Retrieval reranking
- Retrieval evaluation using a test dataset
- Incremental indexing based on content changes
- Vector indexes for larger datasets
- Additional embedding and LLM providers