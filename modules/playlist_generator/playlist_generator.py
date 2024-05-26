import os
import json     
import argparse
import spotipy
import webbrowser
from modules.llm.mistral import chat

from dotenv import load_dotenv
load_dotenv()

# Set OpenAI and Spotify keys directly
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = 'http://localhost:8888/callback'

# Parsing arguments for command line calls
parser = argparse.ArgumentParser(description='Simple command line song utility')
parser.add_argument("--prompt", type=str, help='The prompt to describe the playlist')
parser.add_argument("--numsongs", type=int, default=10, help='The length of the playlist')
parser.add_argument("--playlist-name", type=str, default=argparse.SUPPRESS, help='The name of the playlist')
parser.add_argument("--interactive", action='store_true', default=False, help='Build interactive or automatic playlist')
args = parser.parse_args()
if 'playlist_name' not in args:
    args.playlist_name = args.prompt  # use prompt as playlist name if not specified

separator = f'{100*"-"}'

class SpotifyPlaylist:
    def __init__(self, prompt, length=10, name=None, interactive=False):
        '''
        Create SpotifyPlaylist instance with given parameters
        '''
        self.prompt = prompt
        self.length = int(length)
        self.name = name if name is not None else prompt
        self.interactive = interactive
        self.tracks = []  # list of tracks generated with GPT
        self.playlist_tracks = set()  # list of [artist - song] in my playlist
        self.artists_blacklist = set()  # list of blacklisted artists
        self.songs_blacklist = set()  # list of blacklisted songs
        self.songs_in_playlist = set()  # list of songs already in my playlist

    def __repr__(self):
        '''
        Override print method and returns the contents of my playlist formatted as: 
        #. song_title - artist_name | album name
        '''
        result = f'{separator}\n'
        result += f'Prompt: {self.prompt}\n'
        result += f'Length: {self.length}\n'
        result += f'Name: {self.name}\n'
        result += f'Interactive: {self.interactive}\n'
        if self.artists_blacklist:
            result += f'Artists Blacklist: {self.artists_blacklist}\n'
        if self.songs_blacklist:
            result += f'Songs Blacklist: {self.songs_blacklist}\n'
        result += f'{separator}\n'

        playlist_items = self.sp.playlist_items(self.playlist['id'])['items']
        for id, item in enumerate(playlist_items, start=1):
            artist = item['track']['album']['artists'][0]['name']
            name = item['track']['name']
            album = item['track']['album']['name']
            result += f"{id}. {artist} - {name} | {album}\n"

        result += f'{separator}\n'

        return result
    
    def generate_playlist(self):
        """
        Asks Mistral Large to generate a list of songs based on an input prompt
        """

        playlist_example = """
        [
            {"song": "Hurt", "artist": "Johnny Cash"},
            {"song": "Yesterday", "artist": "The Beatles"},
            {"song": "Someone Like You", "artist": "Adele"},
            {"song": "Nothing Compares 2 U", "artist": "Sinead O'Connor"},
            {"song": "Tears in Heaven", "artist": "Eric Clapton"}
        ]
        """

        user_content = f"Give me {self.length} songs matching this prompt: {self.prompt}"

        bad_songs = str(self.songs_blacklist.union(self.songs_in_playlist))
        if bad_songs:
            user_content += f", which are not part of this list: {bad_songs}"
        
        self.messages = [
            {"role": "system", "content": """You are a Spotify assistant helping the user create music playlists.
            You should generate a list of artists and songs you consider fit the text prompt.
            The output should be a JSON array formatted like this: {"song": <song_title>, "artist": <artist_name>}.
            Do not return anything else than the JSON array."""},
            {"role": "user", "content": "Give me 5 very sad songs"},
            {"role": "assistant", "content": playlist_example},
            {"role": "user", "content": user_content}
        ]

        result = chat(self.messages)
        return json.loads(result)

    def login_to_spotify(self):
        '''
        Connects to Spotify and creates spotipy instance to interact with it
        '''
        self.sp = spotipy.Spotify(
            auth_manager=spotipy.SpotifyOAuth(
                client_id=SPOTIPY_CLIENT_ID,
                client_secret=SPOTIPY_CLIENT_SECRET,
                redirect_uri=SPOTIPY_REDIRECT_URI,
                scope='user-read-playback-state,user-modify-playback-state,playlist-modify-private'
            )
        )
        
        self.current_user = self.sp.current_user()
        assert self.current_user is not None

    def main(self):
        '''
        Main method called to generate the contents and create the Spotify playlist
        '''
        self.login_to_spotify()

        # get all playlist names
        all_playlists = self.sp.user_playlists(self.current_user['id'])
        playlist_names = [p['name'].lower() for p in all_playlists['items']]
        
        # create new playlist with a unique name (adds suffix id if necessary)
        p_name = f'_{self.name}'
        playlist_name = p_name
        id = 1

        while playlist_name.lower() in playlist_names:
            id += 1
            playlist_name = f'{p_name} {str(id)}'
        
        # create and open new playlist
        self.playlist = self.sp.user_playlist_create(self.current_user['id'], public=False, name=playlist_name)
        webbrowser.open(self.playlist['uri'])

        if self.interactive:
            self.fill_playlist_interactive()
        else:
            self.fill_playlist_automatic()
        
        print('>> end of playlist creation')
        
        return

    def fill_playlist_automatic(self):
        '''
        In this mode, the contents of the playlist are generated once and the playlist is filled up
        with the corresponding songs automatically.
        '''

        # asks Mistral to generate the playlist contents
        self.mixer_tracks = self.generate_playlist()
        first_song = None
        
        for item in self.mixer_tracks:
            # extract artist and song
            artist_name = item['artist']
            song_name = item['song']

            # search for title and add it to playlist
            query = f"{artist_name} {song_name}"
            search_results = self.sp.search(q=query, type='track', limit=10)
            song = search_results['tracks']['items'][0]
            track = self.sp.track(song['id'])
            track_id = track['id']
            self.sp.user_playlist_add_tracks(self.current_user['id'], self.playlist['id'], [track_id])
            
            # store first song to play it at the end
            if not first_song:
                first_song = song
        
        # play first song of playlist
        if first_song:
            webbrowser.open(self.playlist['uri'])
            self.play_song_in_spotify(first_song)

    def play_song_in_spotify(self, song, start_position=0):
        '''
        Play a given song in Spotify.

        Args:
            song (Song): song object
            start_position (int): start song at given time in milliseconds
        '''
        
        # get the current Spotify device
        devices = self.sp.devices()['devices']

        # activate device and play song
        self.sp.transfer_playback(devices[0]['id'])
        self.sp.start_playback(uris=[song['uri']], position_ms=start_position)

    def fill_playlist_interactive(self):
        '''
        Fills the contents of the playlist one song at a time. Each song is playing around the middle
        of the track. The user can choose to add the song, ignore the song or ignore the artist. 
        Ignored songs and songs from ignored artists won't be suggested again.
        When all songs suggested by chatGPT have been covered, a new batch can be ordered, and so on.
        '''

        track_id = 0
        build_playlist = True
        first_song = None

        # asks Mistral AI to generate the playlist contents
        self.mistral_tracks = self.generate_playlist()
        
        for item in self.gpt_tracks:

            if not build_playlist:
                break
            
            track_id += 1

            # extract artist and song
            artist_name = item['artist']
            song_name = item['song']
            track_name = f'{artist_name} - {song_name}'
            
            # ignore songs already in playlist
            if track_name in self.playlist_tracks:
                continue 

            # ignore blacklisted artists
            if artist_name in self.artists_blacklist:
                continue
            
            # ignore blacklisted songs
            if song_name in self.songs_blacklist:
                continue
            
            # search for song
            query = f"{item['artist']} {item['song']}"
            search_results = self.sp.search(q=query, type='track', limit=10)
            song = search_results['tracks']['items'][0]
            track = self.sp.track(song['id'])
                        
            # store first song to play it at the end
            if not first_song:
                first_song = song

            # play song in spotify, start in the middle
            start_position = track['duration_ms'] / 2
            self.play_song_in_spotify(song, start_position)
            
            while True:
                match input('Your choice: '):

                    case '1':
                        # Add to Playlist
                        self.sp.user_playlist_add_tracks(self.current_user['id'], self.playlist['id'], [track['id']])
                        self.playlist_tracks.add(track_name)
                        self.songs_in_playlist.add(song_name)
                        print(f'>> added to playlist ({len(self.playlist_tracks)} tracks)')
                        break

                    case '2':
                        # Add song to blacklist
                        self.songs_blacklist.add(song_name)
                        print('>> song blacklisted')
                        break

                    case '3':
                        # Add artist to blacklist
                        self.artists_blacklist.add(artist_name)
                        print('>> artist blacklisted')
                        break

                    case 'q':
                        # Quit playlist creation
                        build_playlist = False
                        break
                    
                    case _:
                        print('Invalid choice. Please enter 1, 2, 3 or q to quit')
        
        if build_playlist:
            # ask user if he wants another batch from chatGPT
            print(separator)
            print('Do you want another batch of songs?')
            print('[1] Yes, give me more songs!')
            print("[2] No, I'm down with this playlist")
            
            while True:
                match input('Your choice: '):

                    case '1':
                        print('>> new batch incoming, please wait...')
                        break
                    case '2':
                        build_playlist = False
                        break
                    case _:
                        print('Invalid choice. Please enter 1 or 2 and hit enter')
        
        if build_playlist:
            # restart the process with a new batch
            self.fill_playlist_interactive()
        else:
            print('>> end of playlist creation')

        # play first song of playlist
        if first_song:
            webbrowser.open(self.playlist['uri'])
            self.play_song_in_spotify(first_song)


if __name__ == '__main__':
    # parsing arguments for command-line calls
    prompt = args.prompt
    length = args.numsongs
    name = args.playlist_name
    interactive = args.interactive

    print(separator)
    print(' SPOTIFY PLAYLIST GENERATOR '.center(100, '-'))
    print(separator)
    print('Creating playlist. Please wait...')
    playlist = SpotifyPlaylist(prompt, length, name, interactive)
    playlist.main()
    print(playlist)
