from typing import Protocol


class Generator(Protocol):
    def generate(
        self,
        question: str,
        context: str
    ) -> str:
        ...