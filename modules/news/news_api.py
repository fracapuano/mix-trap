from modules.llm.mistral import chat, ChatMessage
from dotenv import load_dotenv
from newsapi import NewsApiClient
from modules.news.news_api_domains import trusted_domains
from datetime import datetime, timedelta


load_dotenv()  # take environment variables from .env.

def prepare_news(news: dict) -> str:
    output = ""
    for article in news["articles"]:
        output += f"""
        TITLE: {article["title"]}
        CONTENT: {article["content"]}

        """

    return output

report_prompt = lambda news: f"""
        ### Instruction
        Based on audience and news, produce a short and very clear report of the news you have access to.

        ### News
        {news}
"""
class NewsHandler:
    newsapi = NewsApiClient(api_key='7885465e86e746fead9f8e035a5b395f')
    
    def fetch_news(self, query: str) -> dict:
        all_articles = self.newsapi.get_everything(q=query,
                                              domains=",".join(trusted_domains),
                                              from_param=(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                                              #language='en',
                                              sort_by='relevancy')

        return all_articles
    
    def create_news_report(self, news: dict) -> str:
        processed_news = prepare_news(news)
        report = chat([ChatMessage(role="user", content=report_prompt(processed_news))])
        return report

# Example usage
if __name__ == "__main__":
    # instatiate the news handler client
    news_client = NewsHandler()
    # query the handler for news on a given query
    query = "tesla"
    news_data = news_client.create_news_report(news_client.fetch_news(query))
    print(news_data)

