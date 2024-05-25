import re
from typing import List
from modules.llm.mistral import chat, ChatMessage

def extract_topics(text: str) -> list:
    # Regular expression to find the content between <topics> and </topics>
    match = re.search(r'<topics>(.*?)</topics>', text, re.DOTALL)
    if match:
        topics_str = match.group(1).strip()
        # Split the topics by new lines and return as a list
        topics_list = [topic.strip() for topic in topics_str.split('\n') if topic.strip()]
        return topics_list
    else:
        return []

topics_extraction_prompt = lambda user_conversation: f"""
Here is a conversation between a human user and an AI assistant:

<user_conversation>
{user_conversation}
</user_conversation>

Your task is to carefully read through this conversation and identify the key high-level topics that
the user seems interested in researching or learning more about. Focus on the user's core interests
and avoid getting too granular with the topics.

Once you've identified the key topics, please list them out with each topic on a separate line
inside <topics> tags, like this:

<topics>
Topic 1
Topic 2
Topic 3
</topics>

It's crucial that you extract the most relevant topics, as another AI system will use your output to
search for content related to the user's interests.

After listing out the topics, please provide a brief justification explaining why you chose those
particular topics. Provide your justification inside <justification> tags.

Remember, focus on high-level topics that capture the essence of what the user is curious about. The
goal is to enablethe AI system to find the most relevant and interesting content to continue the
conversation.
"""

def get_topics(user_input: str) -> List[str]:
    
    topics = extract_topics(
        chat([ChatMessage(role="user", content=topics_extraction_prompt(user_input))])
    )

    return topics

if __name__=="__main__":
    user_input = """
    <user>Can you tell me more about the latest advancements in AI and machine learning?</user>
    <assistant>Sure! AI and machine learning have been rapidly evolving. What specific areas are you interested in?</assistant>
    <user>I'm particularly interested in natural language processing and computer vision.</user>
    <assistant>Great! Those are fascinating areas. What do you want to know more about?</assistant>

    """
    topics = get_topics(user_input)
    print(topics)  # Output: ['AI and machine learning', 'Natural language processing', 'Computer vision']
