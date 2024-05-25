from mistralai.models.chat_completion import ChatMessage
from modules.llm.mistral import chat
from modules.news.news_api import fetch_news

SEARCH_PROMPT = f"""
### Instruction

Your task is to write a list of appropriate queries based on user interests, separated by commas.

### Examples

user:
I like movies and AI
response:
movies, Artificial Intelligence

user:
Hey! I'm a Premier League fan and I want to hear about Liverpool and British politics
response:
Premier League, Liverpool, British politics

### Task

"""


def build_report(description: str):
    content = (
        SEARCH_PROMPT
        + f"""
    user:
    {description}
    response:
    """
    )
    raw_topics = chat([ChatMessage(role="user", content=content)]).split(",")
    topics = [raw_topic.strip() for raw_topic in raw_topics]
    news = []
    
    for topic in topics:
        news.append(fetch_news(topic))
    
    report_prompt = f"""
        ### Instruction
        Based on audience and news, produce a short and very clear report of the news you have access to.

        ### Audience
        {description}

        ### News
        {news}
    """
    print("news", news)
    report = chat([ChatMessage(role="user", content=report_prompt)])
    return report


if __name__ == "__main__":
    from time import time
    start = time()
    result = build_report("Sports")
    print(f"Time taken: {time() - start} seconds")
    print("result", result)
