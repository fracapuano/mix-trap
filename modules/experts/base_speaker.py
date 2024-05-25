from modules.llm.mistral import (
    client as mistralclient, 
    ChatMessage, 
    model
)
from modules.news.news_api import NewsHandler
from modules.news.perplexity import topic_to_knowledge


class BaseSpeaker:
    def __init__(self, topic: str):
        self.debate_topic = topic
        self.messages = []
        self.tools = []

        # Add the news handler
        self.news_client = NewsHandler()
    
    def add_message(self, content: str):
        self.messages.append(ChatMessage(role="user", content=content))
    
    def get_news_digest(self, topic: str):
        news_data = self.news_client.create_news_report(topic)
        return news_data
    
    def get_basic_knowledge(self, topic: str):
        """Differently from news, this uses perplexity to generate a short summary of the topic."""
        knowledge = topic_to_knowledge(topic)
        return knowledge
    
    async def reply(self, observation:str):
        self.add_message(observation)
        stream = mistralclient.chat_stream(
        model=model,
        messages=self.messages
        )

        for chunk in stream:
            yield {
                "content": chunk.choices[0].delta.content,
                "content_complete": False
            }

        yield {
            "content": "",
            "content_complete": True,
        }

async def main():
    speaker = BaseSpeaker("French cheese")
    output = ""
    async for content in speaker.reply("What is the best French cheese?"):
        output += content["content"] # This will print each chunk of content as it is received.

    return output

if __name__ == "__main__":
    import asyncio
    a = asyncio.run(main())

    print(a)