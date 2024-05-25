import os
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-large-latest"

client = MistralClient(api_key=api_key)

ALL_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_news",
            "description": "Get the current news",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Keywords or phrases to search for in the article title and body.",
                    }
                },
                "required": ["transaction_id"],
            },
        },
    }
]


def write_news():
    chat([ChatMessage(role="user", content="You task it to write a radio news report. THe target audiance is intested in movies and AI.")])

def chat(messages, tools=[]):
    chat_response = client.chat(
        model=model,
        messages=messages,
        tools=tools
    )
    return chat_response.choices[0].message.content


if __name__ == '__main__':
    result = chat([ChatMessage(role="user", content="What is the best French cheese?")])
    print("result", result)