import os
import requests
from dotenv import load_dotenv
from typing import Dict, Any, NewType

load_dotenv()


url = "https://api.perplexity.ai/chat/completions"
NewsTopic = NewType("NewsTopic", str)
JSONPayload = NewType("JSONPayload", Dict[str, Any])

def create_perplexity_query(topic:NewsTopic, model:str="mixtral-8x7b-instruct") -> JSONPayload:
    """
    Create a query for perplexity to search the internet for a given news topic.

    Args:
        topic (NewsTopic): The news topic for which the perplexity report is generated.
        model (str, optional): The model to use for generating the perplexity scores. Defaults to "mixtral-8x7b-instruct".

    Returns:
        JSONPayload: A dictionary representing the query for generating perplexity scores.
    """
    return {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "Be precise and concise."
            },
            {
                "role": "user",
                "content": f"Give me the latest in topic: {topic}."
            }
        ]
    }

def get_headers() -> JSONPayload:
    """
    Get the headers for the HTTP request to the Perplexity API.

    Returns:
        JSONPayload: A dictionary containing the headers for the HTTP request.
    """
    return {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {os.getenv('PERPLEXITY_API_KEY')}"
    }

def topic_to_knowledge(topic:NewsTopic) -> str:
    """
    Get the latest news for a given topic using the Perplexity API.

    Args:
        topic (NewsTopic): The news topic for which to get the latest news.

    Returns:
        str: The response from the Perplexity API containing the latest news for the given topic.
    """
    payload = create_perplexity_query(topic)
    headers = get_headers()

    response = requests.post(url, json=payload, headers=headers)

    return response.text


if __name__ == "__main__":
    topic = "Artificial Intelligence today"
    news = topic_to_knowledge(topic)
    print(news)
