---
name: learning-knowledge-rag
description: Query indexed learning material using RAG and return grounded answers with sources. Use this skill when a user asks questions about learning material stored in a Learning Knowledge collection.
---

# Learning Knowledge RAG

Use this skill when the user wants to ask questions about indexed learning material.

The knowledge base can contain multiple independent collections, such as courses, PDFs, transcripts, or other learning material.

## Workflow

1. Identify the knowledge collection relevant to the user's question.

2. Use the `ask_knowledge` MCP tool with:
   - The user's question.
   - The selected collection.

3. The tool will:
   - Embed the question.
   - Search only the selected knowledge collection for relevant chunks.
   - Provide the retrieved material to the LLM.
   - Generate an answer grounded in the retrieved context.

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

Each collection represents an independent set of learning material.

Examples:

- `python-course`
- `aws-course`
- `system-design`
- `company-training`

Queries must be scoped to the appropriate collection so that material from unrelated collections is not mixed during retrieval.

## Supported Learning Material

The ingestion system can normalize different learning sources into a common document format.

Currently supported sources include:

- PDF files.
- Text files.
- Directories containing text files.
- Udemy course transcripts when the transcript data is available to the ingestion system.

All supported sources are converted into documents before entering the shared RAG pipeline.

## Grounding Rules

Base the answer on the material retrieved from the selected collection.

If the retrieved context does not contain enough information to answer the question, say that the available learning material does not provide enough information.

Do not invent information that is not supported by the retrieved context.

Do not use material from another collection to fill missing information.

## Expected Output

Provide:

1. A clear answer to the user's question.
2. Relevant examples or code when supported by the learning material.
3. The sources used to answer the question.

## Example

User:

`How do I reverse a string in Python?`

For a Python learning collection, call:

`ask_knowledge(
    question="How do I reverse a string in Python?",
    collection="python-course"
)`

Return the grounded answer together with the retrieved sources.

For another collection, the same tool can be reused:

`ask_knowledge(
    question="What is an IAM role?",
    collection="aws-course"
)`