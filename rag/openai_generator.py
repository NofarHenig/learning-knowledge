from dotenv import load_dotenv
from openai import OpenAI


class OpenAIGenerator:
    def __init__(self):
        load_dotenv()
        self.client = OpenAI()

    def generate(
        self,
        question: str,
        context: str
    ) -> str:
        response = self.client.responses.create(
            model="gpt-5-mini",
            instructions=(
                "Answer the user's question using only the provided context. "
                "If the context does not contain enough information to answer "
                "the question, say that the course material does not provide "
                "enough information."
            ),
            input=f"""
Question:
{question}

Context:
{context}
"""
        )

        return response.output_text