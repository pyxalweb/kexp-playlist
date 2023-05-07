import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time

def remove_duplicate_tracks(playlist_id, client_id, client_secret, redirect_uri, scope):
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                   client_secret=client_secret,
                                                   redirect_uri=redirect_uri,
                                                   scope=scope))

    # Get all tracks in the playlist
    all_tracks = []
    playlist = sp.playlist(playlist_id, fields="tracks,next")
    tracks = playlist['tracks']
    while tracks:
        for item in tracks['items']:
            all_tracks.append((item['track']['id'], item['track']['name'], item['track']['artists'][0]['name']))
        tracks = sp.next(tracks)
    print(f'All tracks: {all_tracks}')

    # Remove duplicate tracks from the playlist
    removed_tracks = []
    for track in all_tracks:
        track_id, title, artist = track
        # if there is more than 1 of the same track
        if all_tracks.count(track) > 1 and track_id not in removed_tracks:
            sp.playlist_remove_all_occurrences_of_items(playlist_id, [track_id])
            removed_tracks.append(track_id)
            print(f'Removing duplicate track: {title} - {artist}')
            print('Waiting 5 seconds')
            time.sleep(5)

    # Add cleaned tracks back to the playlist
    cleaned_tracks = [track for track in all_tracks if track[0] not in removed_tracks]
    songs_added = 0
    for track in cleaned_tracks:
        track_id, title, artist = track
        sp.playlist_add_items(playlist_id, [track_id])
        songs_added += 1
        print(f'Added {title} by {artist} to playlist')
        print('Waiting 5 seconds')
        time.sleep(5)

    print(f'Total songs in playlist: {len(all_tracks)}')
    print(f'Songs removed from playlist: {len(removed_tracks)}')
    print(f'Songs added to playlist: {songs_added}')

remove_duplicate_tracks('XXXXXXXXXXXXXXXXXXXXXX', 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX', 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX', 'http://127.0.0.1:8080', 'playlist-modify-public')

