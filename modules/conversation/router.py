from modules.llm.async_groq_mistral import chat as groq_chat


class Router:
    def __init__(self):
        self.conversation_buffer = []
        self.add_message(
            {
                "role": "system",
                "content": """
                Your goal is to serve as a router for the conversation. 
                You are a crucial component in the system we built in the sense that it is your
                responsability to extract from the user instructions which part of our system 
                they wish to interact with.

                Possible choices are:
                - 1. News broadcast
                - 2. Deep diving on a specific news topic
                - 3. Playlist creation

                You always answer with one number only, meaning that your output can and will always
                be either 1, 2 or 3. 
                1 is for news broadcast, 2 is for deep diving on a specific news topic and 3
                is for playlist creation.
                """
            }
        )

    def add_message(self, message):
        self.conversation_buffer.append(message)
    
    def get_current_intent(self, message:str):
        current_message_formatted = dict(role="user", content=message)
        return groq_chat(
            messages=[self.conversation_buffer[0], current_message_formatted]
        )

if __name__ == "__main__":
    router = Router()
    message = "play me some happy music"
    router.add_message({"role": "user", "content": message})
    
    async def main():    
        stream = router.get_current_intent(message)

        output = ""
        async for chunk in stream:
            print(chunk, end="")

    import asyncio
    asyncio.run(main())
