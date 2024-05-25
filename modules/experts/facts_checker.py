import re
from modules.experts.base_speaker import BaseSpeaker
from modules.llm.mistral import chat, ChatMessage
from icecream import ic

fact_checking_prompt = lambda basic_knowledge, latest_news, point_at_issue: f"""
Here is some basic knowledge about the topic:
<basic_knowledge>
{basic_knowledge}
</basic_knowledge>

Here are the latest news articles related to the topic:
<latest_news>
{latest_news}
</latest_news>

The specific point about the topic to address is:
<point_at_issue>
{point_at_issue}
</point_at_issue>

Carefully review the basic knowledge, latest news, and specific point at issue provided above.

In a <scratchpad> section, write out your analysis of the topic. Draw connections between the basic
knowledge, latest news, and the point at issue to generate relevant insights. Consider how the
latest news builds upon or changes the basic knowledge. Analyze what the latest news reveals about
the specific point at issue.

<scratchpad>

</scratchpad>

Based on your analysis above, provide a concise, thoroughly fact-based insight that addresses the
specific point at issue. Cite the most relevant facts from the basic knowledge and latest news to
support your insight. Write the insight inside <insight> tags.
"""

def extract_insights(text: str) -> list:
    # Regular expression to find the content between <topics> and </topics>
    match = re.search(r'<insight>(.*?)</insight>', text, re.DOTALL)
    if match:
        topics_str = match.group(1).strip()
        # Split the topics by new lines and return as a list
        topics_list = [topic.strip() for topic in topics_str.split('\n') if topic.strip()]
        return topics_list
    else:
        return []

class FactsChecker(BaseSpeaker):
    def __init__(self, topic: str):
        super().__init__(topic=topic)

    def fact_check(self, point_at_issue: str):
        """Differently from news, this uses perplexity to generate a short summary of the topic."""
        knowledge, thelatest = self.get_basic_knowledge(point_at_issue), self.get_news_digest(point_at_issue)

        return chat(
            [ChatMessage(role="user", content=fact_checking_prompt(knowledge, thelatest, point_at_issue))]
        )

if __name__ == "__main__":
    topic = "Should the government provide free healthcare for all citizens?"
    fact_checker = FactsChecker(topic)
    
    result = fact_checker.fact_check("Public healthcare is a human right.")
    print(extract_insights(result)[0])