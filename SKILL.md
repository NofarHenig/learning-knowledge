---
name: learning-material-rag
description: Ask questions about indexed learning materials using RAG and receive grounded answers with sources. Use this skill when a user wants to query PDFs, notes, courses, documentation, or other material stored in a Learning Material RAG collection.
---

# Learning Material RAG

Use this skill when the user wants to ask questions about learning material that has already been indexed into a Learning Material RAG collection.

The knowledge base can contain multiple independent collections, such as courses, PDFs, notes, documentation, or other learning material.

## Workflow

1. Identify the knowledge collection relevant to the user's question.

2. Use the `ask_knowledge` MCP tool with:
   - The user's question.
   - The selected collection.

3. The tool retrieves relevant material only from the selected collection and generates an answer grounded in that material.

4. Return the generated answer to the user.

5. Include the sources returned by the tool.

## MCP Tool

Use:

`ask_knowledge(question, collection)`

Parameters:

- `question`: The user's question.
- `collection`: The knowledge collection that should be searched.

The tool returns:

- A grounded answer.
- The sources retrieved from the selected collection.

## Knowledge Collections

Each collection represents an independent set of indexed learning material.

Examples:

- `python-course`
- `aws-course`
- `system-design`
- `company-training`

Queries must be scoped to the appropriate collection so that material from unrelated collections is not mixed during retrieval.

If the appropriate collection cannot be determined, ask the user which collection should be used rather than guessing.

## Supported Learning Material

The Learning Material RAG ingestion pipeline can normalize different learning sources into a common document format before indexing.

Currently supported sources include:

- PDF files.
- Text files.
- Directories containing text files.

The architecture is designed so additional source adapters can be added without changing the shared RAG pipeline.

The Skill queries material that has already been indexed. It does not download or ingest new learning material itself.

## Grounding Rules

Base the answer only on material retrieved from the selected collection.

If the retrieved context does not contain enough information to answer the question, clearly say that the available learning material does not provide enough information.

Do not invent information that is not supported by the retrieved context.

Do not use material from another collection to fill missing information.

## Expected Output

Provide:

1. A clear answer to the user's question.
2. Relevant examples or code when supported by the retrieved learning material.
3. The sources returned by the tool.

## Example

User:

`How do I reverse a string in Python?`

For a Python learning collection, call:

`ask_knowledge(
    question="How do I reverse a string in Python?",
    collection="python-course"
)`

Return the grounded answer together with the retrieved sources.

The same tool can be reused for another collection:

`ask_knowledge(
    question="What is an IAM role?",
    collection="aws-course"
)`