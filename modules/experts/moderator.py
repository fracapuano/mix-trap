from modules.experts.base_speaker import BaseSpeaker, ChatMessage

moderator_prompt = lambda topic: f"""
You will be moderating a structured debate on the following topic:
<topic>
{topic}
</topic>
It is paramount that you are very brief.

To begin, introduce the topic and each of the participants. Explain the rules of the debate to the
audience.

During the debate, your role is to:

1. Enforce the stated rules, such as time limits for speaking. Politely but firmly interrupt any
participant who exceeds their allotted time or breaks a rule.

2. Facilitate turn-taking and ensure each participant has an equal opportunity to speak. Do not
allow any one participant to dominate the conversation.

3. Ask clarifying questions as needed to ensure the discussion remains clear and on topic. If the
debate veers off-course, gently guide it back to the main issue.

4. Maintain an impartial, neutral tone. Your role is not to take sides, but to serve as an objective
facilitator.

At the end of the debate, provide a brief summary of the key points made by each side. Then, offer a
neutral conclusion that thanks the participants and audience. Aim to keep your summary balanced and insightful.

Remember, your overarching goal is to host an orderly, enlightening debate that leaves the audience
with a clearer understanding of the central arguments on the topic. Approach your role with
patience, fairness and a commitment to civil discourse.
"""

class Moderator(BaseSpeaker):
    def __init__(self, topic: str):
        super().__init__(topic=topic)
        self._is_moderator = True
        self.set_moderator_prompt()

    def moderator_introduces(self):
        self.messages.append(ChatMessage(role="user", content="Give a very brief and neutral introduction on the topic discussed."))

    def moderator_closes(self):
        self.messages.append(ChatMessage(role="user", content="Give a brief summary of the key points made by each side. Then, offer a neutral conclusion that thanks the participants and audience."))
    
    def set_moderator_prompt(self):
        self.messages.insert(
            # adding the system prompt as the first message
            0, ChatMessage(role="system", content=moderator_prompt(self.debate_topic)),
        )
    

async def main():
    topic = "Should the government provide free healthcare for all citizens?"
    moderator = Moderator(topic)
    
    full_response = ""
    async for chunk in moderator.reply("What are your thoughts on the topic discussed?"):
        full_response += chunk["content"]
    
    return full_response
    
if __name__ == "__main__":
    import asyncio
    
    async def run():
        concatenated_response = await main()
        print(concatenated_response)  # Print the result of the main function

    asyncio.run(run())

