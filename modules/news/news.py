import os
import requests
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.


def fetch_news(query):
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        raise ValueError(
            "No API key found. Please set the NEWS_API_KEY environment variable."
        )

    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={api_key}&pageSize=2"

    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()


# Example usage
if __name__ == "__main__":
    query = "tesla"
    news_data = fetch_news(query)
    print(news_data)
