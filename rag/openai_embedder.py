from dotenv import load_dotenv
from openai import OpenAI


class OpenAIEmbedder:
    def __init__(self):
        load_dotenv()
        self.client = OpenAI()

    def embed(self, texts: list[str]) -> list[list[float]]:
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=texts
        )

        embeddings = []

        for item in response.data:
            embeddings.append(item.embedding)

        return embeddings