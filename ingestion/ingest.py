from .source import ContentSource, Document

def ingest(source: ContentSource) -> list[Document]:
    return source.load()