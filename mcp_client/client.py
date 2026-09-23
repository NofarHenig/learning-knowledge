import asyncio
import os
import sys

from dotenv import load_dotenv
from mcp import Client, StdioServerParameters


load_dotenv()


async def main():
    collection = os.getenv("KNOWLEDGE_COLLECTION")

    if not collection:
        raise ValueError(
            "KNOWLEDGE_COLLECTION is not configured"
        )

    question = input("Enter your question: ")

    server = StdioServerParameters(
        command=sys.executable,
        args=["-m", "mcp_server.server"],
        env={
            "OPENAI_API_KEY": os.environ["OPENAI_API_KEY"],
            "POSTGRES_CONNECTION_STRING": os.environ[
                "POSTGRES_CONNECTION_STRING"
            ]
        }
    )

    async with Client(server) as client:
        tools = await client.list_tools()

        print("\nAvailable tools:")

        for tool in tools.tools:
            print(f"- {tool.name}")

        result = await client.call_tool(
            "ask_knowledge",
            {
                "question": question,
                "collection": collection
            }
        )

        print("\nCollection:")
        print(collection)

        print("\nAnswer:")

        for content in result.content:
            if hasattr(content, "text"):
                print(content.text)


if __name__ == "__main__":
    asyncio.run(main())