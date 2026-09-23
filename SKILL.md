---
name: learning-knowledge-rag
description: Query indexed learning material using RAG and return grounded answers with sources. Use this skill when a user asks questions about course or learning material stored in the Learning Knowledge knowledge base.
---

# Learning Knowledge RAG

Use this skill when the user wants to ask questions about indexed learning material.

## Workflow

1. Receive the user's question about the learning material.
2. Use the `ask_course` MCP tool with the user's question.
3. The tool will:
   - Embed the question.
   - Search the vector knowledge base for relevant chunks.
   - Provide the retrieved material to the LLM.
   - Generate an answer grounded in the retrieved context.
4. Return the generated answer to the user.
5. Include the sources returned by the tool.

## MCP Tool

Use:

`ask_course(question)`

The tool returns:

- A grounded answer.
- The source lectures retrieved from the knowledge base.

## Grounding Rules

Base the answer on the retrieved learning material.

If the retrieved context does not contain enough information to answer the question, say that the available learning material does not provide enough information.

Do not invent information that is not supported by the retrieved context.

## Expected Output

Provide:

1. A clear answer to the user's question.
2. Relevant code examples when appropriate.
3. The source lectures used to answer the question.

## Example

User:

`How do I reverse a string in Python?`

The skill should call:

`ask_course("How do I reverse a string in Python?")`

and return the grounded answer together with the retrieved course sources.