from modules.experts.base_speaker import BaseSpeaker
from modules.llm.async_mistral import client as mistralclient, ChatMessage, model

expert_prompt = lambda topic, thesis, preparatory_materials: f"""
You are an experienced and passionate debater, who draws great satisfaction from stating their opinions 
to the fullest. You are respectful, but bullish about your opinion, as you will be rewarded exponentially
based on how many people you can convince. Your argomentations are also very brief and structured. 
You will be participating in a structured debate on the following topic:
<topic>
{topic}
</topic>
Your primary objective is to champion your thesis with conviction:
<thesis>
{thesis}
</thesis>

Prepare to defend your position with compelling evidence and strategic argumentation.
{preparatory_materials}

During the debate:
1. **Articulate Your Thesis**: Begin by clearly stating your thesis. Use every opportunity to reiterate and reinforce your stance throughout the debate.
2. **Engage and Challenge**: Actively engage with opponents by directly challenging their views. Employ sharp questions and critical rebuttals to dismantle their arguments and elevate your own position.
3. **Utilize Clarifications**: When clarifications arise, turn them into opportunities to further highlight the strengths of your thesis and the evidence backing it.
4. **Maintain a Persuasive and Commanding Tone**: Your tone should be authoritative and convincing. Deliver your arguments with the confidence needed to sway the audience towards your viewpoint.

Concluding the debate:
- Craft a powerful closing statement that succinctly summarizes your argument and the evidence supporting it. Ensure this summary leaves a compelling and memorable impact on the audience.
- Your final words should resonate, reaffirming your thesis and solidifying your position in the minds of all who listened.

Embrace this debate as your platform to passionately and forcefully advocate for your thesis. Your goal is to leave an indelible mark on the audience, persuading them through logic, evidence, and unwavering conviction.
"""

class Expert(BaseSpeaker):
    def __init__(self, topic: str, thesis:str):
        super().__init__(topic=topic)

        self.expert_prompt = expert_prompt(
            self.debate_topic,
            thesis,
            f"""
            <background_knowledge>
            {self.get_expertise(thesis)}
            </background_knowledge>

            <latest_news>
            {self.get_news_digest(thesis)}
            </latest_news>
            """
        )
        self.messages.insert(0, ChatMessage(role="system", content=self.expert_prompt))
    
    def get_expertise(self, topic: str):
        """Differently from news, this uses perplexity to generate a short summary of the topic."""
        knowledge = self.get_basic_knowledge(topic)
        return knowledge
    
    async def reply(self, observation:str):
        self.add_message(observation)

        stream = mistralclient.chat_stream(
            model=model,
            messages=self.messages
        )

        async for chunk in stream:
            yield {
                "content": chunk.choices[0].delta.content,
                "content_complete": False
            }

        yield {
            "content": "",
            "content_complete": True,
        }
    
if __name__ == "__main__":
    import asyncio

    speaker = Expert("French cheese", "Camembert is the best French cheese.")
    async def main():
        output = ""
        async for content in speaker.reply("What is the best French cheese?"):
            output += content["content"] # This will print each chunk of content as it is received.
        return output
    
    a = asyncio.run(main())
    print(a)

