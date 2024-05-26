from dotenv import load_dotenv
from groq import AsyncGroq

load_dotenv()

model = "mixtral-8x7b-32768"
client = AsyncGroq()  # automatically reads GROQ_API_KEY from .env

async def chat(messages):
    # stream the completion answer
    stream = await client.chat.completions.create(
        messages=messages,
        model=model,
        stream=True,
    )

    async for chunk in stream:
        yield chunk.choices[0].delta.content

if __name__=="__main__":
    chat_stream = chat([
        {"role": "system", "content": "Hello, how can I help you today?"}
    ])
    async def main():
        async for chunk in chat_stream:
            print(chunk, end="")
    
    import asyncio
    asyncio.run(main())