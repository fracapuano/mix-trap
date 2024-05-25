import spotipy
from spotipy.oauth2 import SpotifyOAuth

scope = "user-library-read"
client_id = '5303e33961234c87a5e905d20d1adc7b'
client_secret = 'e0876860743a43ffbbba83754effd5c5'

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, scope=scope))

results = sp.current_user_saved_tracks()
for idx, item in enumerate(results['items']):
    track = item['track']
    print(idx, track['artists'][0]['name'], " – ", track['name'])