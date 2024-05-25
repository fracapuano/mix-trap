from modules.llm.mistral import (
    client as mistralclient, 
    ChatMessage, 
    model
)

class BaseSpeaker:
    def __init__(self, topic: str):
        self.debate_topic = topic
        self.messages = []
        self.tools = []
    
    def add_message(self, content: str):
        self.messages.append(ChatMessage(role="user", content=content))
    
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