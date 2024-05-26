from modules.llm.async_groq_mistral import chat as groq_chat
from modules.experts.anchorman import Anchorman
from modules.experts.journalist import Journalist
from router import Router
from modules.playlist_generator.playlist_generator import SpotifyPlaylist


def create_playlist_from_prompt(prompt):
    SpotifyPlaylist(prompt=prompt, name="Mistral Hackathon", interactive=True).main()

    return  # creates the playlist in my spotify account

class Conversation:
    def __init__(self):
        self.messages = []
        # this is the conversation router directing to the different modules of the radio
        self.router = Router()
        # these are the components of the radio
        self.anchorman = Anchorman()
        self.journalist = Journalist()
        

