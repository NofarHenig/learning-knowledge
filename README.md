# Learning Knowledge RAG

A reusable Retrieval-Augmented Generation (RAG) system that turns learning material into searchable knowledge collections and exposes them to AI clients through MCP.

The project was initially built using Python course transcripts and later generalized to support multiple content sources and independent knowledge collections.

## Architecture

```text
Learning Material
      |
      v
Source Factory
      |
      +---- PDF
      |
      +---- TXT
      |
      +---- Directory
      |
      +---- Udemy Transcripts
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
Knowledge Collections
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

### 1. Generic Ingestion

Learning material is converted into a common `Document` representation containing text and metadata.

The ingestion layer currently supports:

- PDF files
- Text files
- Directories containing text files
- Udemy course transcripts when transcript data is available

A `SourceFactory` selects the appropriate loader based on the provided source.

Each loader returns the same representation:

```text
list[Document]
```

This keeps the rest of the RAG pipeline independent from the original content source.

### 2. Knowledge Collections

Indexed material is organized into independent knowledge collections.

For example:

```text
python-course
aws-course
system-design
company-training
```

Each document and chunk is associated with a collection.

Queries are scoped to a selected collection so unrelated learning material is not mixed during retrieval.

### 3. Chunking

Documents are split into smaller chunks before indexing.

Each chunk preserves the metadata of its original document, including information such as its collection, source, title, and page when available.

### 4. Embeddings

Chunks are converted into vector embeddings using OpenAI embeddings.

The same embedding model is used to convert user questions into vectors so that semantically related content can be retrieved.

### 5. Vector Search

Embeddings are stored in PostgreSQL using the pgvector extension.

When a question is asked, the system searches only the selected collection and uses cosine distance to retrieve the most semantically relevant chunks.

```text
Question
   |
   v
Embedding
   |
   v
Selected Collection
   |
   v
Vector Similarity Search
   |
   v
Top-K Relevant Chunks
```

### 6. RAG Generation

The retrieved chunks are provided to the LLM as context.

The model is instructed to answer using only the retrieved learning material and to report when the available context is insufficient.

The result contains both the generated answer and the retrieved source information.

### 7. MCP

The RAG pipeline is exposed through a Model Context Protocol (MCP) server.

The main MCP tool is:

```text
ask_knowledge(question, collection)
```

For example:

```text
ask_knowledge(
    question="How do I reverse a string in Python?",
    collection="python-course"
)
```

This keeps the RAG implementation independent from a specific AI application and allows MCP-compatible clients or agents to use the knowledge base as a tool.

## Example

Given a Python learning collection:

```text
Question:
How do I reverse a string in Python?

Collection:
python-course
```

The flow is:

```text
Question
   |
   v
Embedding
   |
   v
Search python-course
   |
   v
Top-K Chunks
   |
   v
LLM
   |
   v
Answer + Sources
```

Example retrieved sources:

```text
Methods and Functions Homework - Solutions
Methods and Functions Homework Overview
Function Practice - Solutions Level One
```

The same pipeline can query a completely different collection without changing the RAG implementation:

```text
Question:
What is an IAM role?

Collection:
aws-course
```

## Adding Learning Material

The ingestion pipeline accepts a source and a collection name through configuration.

For example, to index a PDF:

```text
KNOWLEDGE_COLLECTION=aws-course
KNOWLEDGE_SOURCE=materials/aws.pdf
```

The system automatically selects the PDF loader and runs:

```text
PDF
 |
 v
Documents
 |
 v
Chunks
 |
 v
Embeddings
 |
 v
aws-course
```

A text file or directory can be indexed through the same pipeline by changing `KNOWLEDGE_SOURCE`.

Udemy transcript ingestion is also supported when transcript data is available to the ingestion system. The project does not assume that arbitrary Udemy course URLs can be downloaded automatically.

## Tech Stack

- Python
- OpenAI API
- PostgreSQL
- pgvector
- Docker / Docker Compose
- Model Context Protocol (MCP)
- pypdf

## Project Structure

```text
learning-knowledge/
├── ingestion/
│   ├── source.py
│   ├── ingest.py
│   ├── source_factory.py
│   ├── text_source.py
│   ├── directory_source.py
│   ├── pdf_source.py
│   └── udemy_source.py
│
├── rag/
│   ├── chunker.py
│   ├── embedder.py
│   ├── generator.py
│   ├── openai_embedder.py
│   ├── openai_generator.py
│   ├── vector_store.py
│   ├── postgres_vector_store.py
│   └── rag_pipeline.py
│
├── mcp_server/
│   └── server.py
│
├── mcp_client/
│   └── client.py
│
├── db/
│   └── init.sql
│
├── materials/
├── ingest.py
├── ask.py
├── SKILL.md
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## Configuration

Create a `.env` file based on `.env.example`:

```text
OPENAI_API_KEY=your_openai_api_key_here
POSTGRES_CONNECTION_STRING=postgresql://raguser:ragpassword@localhost:5432/learning_knowledge
KNOWLEDGE_COLLECTION=python-course
KNOWLEDGE_SOURCE=udemy
```

For a PDF collection:

```text
KNOWLEDGE_COLLECTION=aws-course
KNOWLEDGE_SOURCE=materials/aws.pdf
```

Never commit the real `.env` file or API keys.

## Running the Project

Start PostgreSQL:

```bash
docker compose up -d postgres
```

Build the ingestion image:

```bash
docker compose build ingest
```

Index the configured learning material:

```bash
docker compose run --rm ingest
```

Run the MCP client:

```bash
python -m mcp_client.client
```

Then enter a question about the selected knowledge collection.

## Design Decisions

### Source-Agnostic Ingestion

Content-specific loaders are isolated behind a shared document representation.

The RAG pipeline therefore does not need to know whether the original material came from a PDF, text file, directory, or course transcript.

### Multi-Collection Retrieval

Multiple independent knowledge bases can coexist in the same vector database.

Retrieval is explicitly scoped to a collection to prevent unrelated learning material from being mixed into the context.

### Dependency Inversion

The RAG pipeline depends on abstractions for:

- `Embedder`
- `VectorStore`
- `Generator`

Concrete implementations such as OpenAI and PostgreSQL/pgvector can therefore be replaced without changing the core RAG orchestration.

### Separate Indexing and Querying

Indexing and querying are separate flows.

Learning material can be processed offline, while questions are served against an already indexed knowledge base.

### Deterministic Chunk IDs

Chunk IDs are generated deterministically from the collection, metadata, and content.

PostgreSQL uses UPSERT operations so repeated ingestion of the same material does not create duplicate chunks.

### Batched Embeddings

Embedding requests are processed in batches to reduce the number of API requests and support larger knowledge bases more efficiently.

### Grounded Generation

Retrieved chunks are supplied to the LLM as context.

The generator is instructed not to answer beyond the retrieved material when sufficient information is unavailable.

## Skill

`SKILL.md` describes how an AI agent should use the knowledge system.

The Skill uses the MCP tool:

```text
ask_knowledge(question, collection)
```

This separates three concerns:

```text
Skill
  |
  | instructions / workflow
  v
MCP
  |
  | tool interface
  v
RAG
  |
  | retrieval + generation
  v
Knowledge Collections
```

## Future Improvements

- YouTube transcript loader
- More automated course-content acquisition
- Local caching of source transcripts
- Token-aware chunking
- Chunk overlap
- Retrieval reranking
- Retrieval evaluation using a golden dataset
- Incremental indexing based on content changes
- HNSW or IVFFlat vector indexes for larger datasets
- Additional embedding and LLM providers
- Improved source citations
- Remote deployment of the MCP service