import re

from ingestion.source import Document


def chunk_document(
    document: Document,
    chunk_size: int = 1000
) -> list[Document]:

    sentences = re.split(r"(?<=[.!?])\s+", document.text)

    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= chunk_size:
            if current_chunk:
                current_chunk += " "

            current_chunk += sentence
        else:
            if current_chunk:
                metadata = document.metadata.copy()
                metadata["chunk_index"] = len(chunks)

                chunks.append(
                    Document(
                        text=current_chunk,
                        metadata=metadata
                    )
                )

            current_chunk = sentence

    if current_chunk:
        metadata = document.metadata.copy()
        metadata["chunk_index"] = len(chunks)

        chunks.append(
            Document(
                text=current_chunk,
                metadata=metadata
            )
        )

    return chunks