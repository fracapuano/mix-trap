import os
from mistralai.async_client import MistralAsyncClient as MistralClient
from mistralai.models.chat_completion import ChatMessage

from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-large-latest"

client = MistralClient(api_key=api_key)

async def chat_async(messages, tools=[]):
    # With async
    async_response = client.chat_stream(
        model=model, 
        messages=messages, 
        tools=tools
    )

    async for chunk in async_response: 
        yield chunk.choices[0].delta.content
