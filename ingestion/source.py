from dataclasses import dataclass
from typing import Protocol


@dataclass
class Document:
    text: str
    metadata: dict


class ContentSource(Protocol):
    def load(self) -> list[Document]:
        ...