import os
import requests
from dotenv import load_dotenv
from newsapi import NewsApiClient
from modules.news.news_api_domains import trusted_domains
from datetime import datetime, timedelta


load_dotenv()  # take environment variables from .env.

class NewsHandler:
    newsapi = NewsApiClient(api_key='7885465e86e746fead9f8e035a5b395f')
    
    def fetch_news(self, query: str) -> dict:
        all_articles = self.newsapi.get_everything(q=query,
                                              domains=trusted_domains,
                                              from_param=(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                                              language='en',
                                              sort_by='relevancy')

        return all_articles

# Example usage
if __name__ == "__main__":
    # instatiate the news handler client
    news_client = NewsHandler()
    # query the handler for news on a given query
    query = "tesla"
    news_data = news_client.fetch_news(query)
    print(news_data)
