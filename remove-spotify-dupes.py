import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time

def remove_duplicate_tracks(playlist_id, client_id, client_secret, redirect_uri, scope):
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                   client_secret=client_secret,
                                                   redirect_uri=redirect_uri,
                                                   scope=scope))

    # Get all tracks from the playlist
    all_tracks = []
    playlist = sp.playlist(playlist_id, fields="tracks,next")
    tracks = playlist['tracks']
    while tracks:
        for item in tracks['items']:
            all_tracks.append((item['track']['name'], item['track']['artists'][0]['name'], item['track']['id']))
        tracks = sp.next(tracks)

    # Remove duplicate tracks from the playlist and add one instance of each track back to the playlist
    duplicate_tracks = set([x for x in all_tracks if all_tracks.count(x) > 1])
    if duplicate_tracks:
        for track in duplicate_tracks:
            track_ids_to_remove = [x[2] for x in all_tracks if x[0] == track[0] and x[1] == track[1]]
            sp.playlist_remove_all_occurrences_of_items(playlist_id, track_ids_to_remove)
            sp.playlist_add_items(playlist_id, [track[2]])
            print (f"Removed {track[0]} by {track[1]} from the playlist. Waiting 5 seconds to avoid rate limiting.")
            time.sleep(5)

    print(f"Removed {len(duplicate_tracks)} duplicate tracks from the playlist.")

remove_duplicate_tracks('XXXXXXXXXXXXXXXXXXXXXX', 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX', 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX', 'http://127.0.0.1:8080', 'playlist-modify-public')
