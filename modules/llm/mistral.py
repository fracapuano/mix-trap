import os
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-large-latest"

client = MistralClient(api_key=api_key)


def chat(messages, tools=[]):
    chat_response = client.chat(
        model=model,
        messages=messages,
        tools=tools,
    )
    print("chat_response", chat_response)
    return chat_response.choices[0].message.content


if __name__ == "__main__":
    result = chat([ChatMessage(role="user", content="What is the best French cheese?")])
    print("result", result)
