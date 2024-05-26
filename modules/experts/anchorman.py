from modules.experts.base_speaker import BaseSpeaker
from modules.llm.async_mistral import client as mistralclient, ChatMessage, model

news_broadcaster_prompt = lambda topic, news_content: f"""
You are an intelligent and insightful news broadcaster, trained to deliver the latest and most relevant news succinctly and engagingly. Your role is to inform the audience about the latest developments in various topics, especially:
<topic>
{topic}
</topic>

Here's what's happening:
{news_content}

Your delivery should be clear, factual, and neutral, aiming to provide the audience with a comprehensive understanding of the events without any bias.
"""

class Archorman(BaseSpeaker):
    def __init__(self, topic: str):
        super().__init__(topic=topic)
        self.news_content = self.get_news_digest(topic)
        self.knowledge_content = self.get_basic_knowledge(topic)
        
        self.broadcaster_prompt = news_broadcaster_prompt(
            self.debate_topic,
            self.news_content
        )
        self.messages.insert(0, ChatMessage(role="system", content=self.broadcaster_prompt))

if __name__ == "__main__":
    import asyncio

    broadcaster = Archorman("AI and Technology")
    async def main():
        output = ""
        async for content in broadcaster.reply("what are the latest "):
            output += content["content"]  # This will print each chunk of content as it is received.
        return output

    broadcast_output = asyncio.run(main())
    print(broadcast_output)