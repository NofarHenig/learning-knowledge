---
name: learning-material-rag
description: Add learning materials to a knowledge collection and ask grounded questions about them using RAG. Use this skill when a user wants to store or query notes, documentation, course material, or other text-based learning content.
---

# Learning Material RAG

Use the Learning Material RAG MCP server to add learning content to knowledge collections and ask questions grounded in that content.

## Available tools

### add_knowledge

Use `add_knowledge` when the user wants to add new text-based material to the knowledge base.

Required inputs:

- `text` — the content to index
- `filename` — a descriptive source name
- `collection` — the knowledge collection where the content should be stored

Example:

User:
> Add these notes to my Python collection.

Call:

`add_knowledge(text=..., filename="python-notes.txt", collection="python")`

After the material is indexed, it can immediately be queried with `ask_knowledge`.

### ask_knowledge

Use `ask_knowledge` when the user asks a question about material that has already been indexed.

Required inputs:

- `question` — the user's question
- `collection` — the collection to search

Example:

User:
> What does my Python material say about decorators?

Call:

`ask_knowledge(question="What does the material say about decorators?", collection="python")`

Return the grounded answer and the sources provided by the tool.

## Workflow

When the user provides new learning material:

1. Determine the appropriate collection.
2. Call `add_knowledge`.
3. Confirm that the material was added.
4. Use `ask_knowledge` for questions about that material.

When the user asks a question about existing material:

1. Identify the relevant collection.
2. Call `ask_knowledge`.
3. Return the answer and its sources.

Do not answer from general knowledge when the user specifically asks for an answer based on the indexed material. If the knowledge base does not contain enough information, say so.