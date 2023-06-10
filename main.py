from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import re
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
print('Dependencies imported successfully.')

options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)
print('Chrome WebDriver is ready.')

driver.get('https://www.kexp.org/playlist/')
print('Selenium has the URL ready.')

max_loops = 5
loop_count = 1
print(f'Scraping {max_loops} playlist page(s).')

scraped_count = 0

scrapedTracks = []

while loop_count <= max_loops:
    try:
        time.sleep(5)

        page_source = driver.page_source
        print('---------------------------------------------------------------------------------------------------\n'
              f'Page {loop_count} of {max_loops}.\n'
              'Selenium has the page source.')

        soup = BeautifulSoup(page_source, 'html.parser')
        print('BeautifulSoup has parsed the HTML.')

        # Find the parent div and child divs
        parent_div = soup.find('div', id='playlist-plays')
        playlist_items = parent_div.find_all('div', class_='PlaylistItem')
        print('Found playlist items!')

        # Loop through the child divs
        for playlist_item in playlist_items:
            # Find the div which contains the track name, artist name, and year
            primary_content_div = playlist_item.find('div', class_='PlaylistItem-primaryContent')
            print('Found content within a playlist item.')

            # If the 'PlaylistItem-primaryContent' div does not contain the appropriate text (track name, artist name, year) then it is likely a sponsor, air break, etc and should be skipped
            if primary_content_div.find('h3', class_='u-mb0' != None) and (primary_content_div.find('div', class_='u-mb1') != None) and (primary_content_div.find_all('div', class_='u-h5') != []):
                # Get the track name, artist name, and year
                track = primary_content_div.find('h3', class_='u-mb0').get_text(strip=True)
                artist = primary_content_div.find('div', class_='u-mb1').get_text(strip=True)
                year = primary_content_div.find_all('div', class_='u-h5')[-1].get_text(strip=True)
                # If the year is matched, then proceed
                if re.match('^2023', year):
                    # Add it to the array
                    scrapedTracks.append((track, artist))
                    scraped_count += 1
                    print('******************************************************************\n'
                    f'Added {track} by {artist} to array.\n'
                    '******************************************************************')
        print(f'Total tracks scraped: {scraped_count}.')

        # Click the 'previous' link to go to the next playlist page
        previous_link = driver.find_element(By.ID, "previous")
        previous_link.click()

        # Add 1 to the loop_count
        loop_count += 1
    except Exception as e:
        print('Error:', e)
        break
    
driver.quit()

print(f'Scraped the following tracks: {scrapedTracks}')

#####################################
# Spotify #
#####################################
def add_to_spotify_playlist(playlist_id, client_id, client_secret, redirect_uri, scope, scraped_count):
    try:
        #####################################
        # Authenticate with Spotify #
        #####################################
        # This fixes the annoying cache notification in the CL
        cache_path = os.path.join('.cache', f'spotipy_{os.getpid()}')

        auth_manager = SpotifyOAuth(client_id=client_id,
                                    client_secret=client_secret,
                                    redirect_uri=redirect_uri,
                                    scope=scope,
                                    cache_path=cache_path)
        sp = spotipy.Spotify(auth_manager=auth_manager)

        print('Successfully authenticated with Spotify.')
    except Exception as e:
        print('Error authenticating with Spotify:', e)

    try:
        #####################################
        # Import tracks to Spotify Playlist #
        #####################################
        # Create a list to store the Spotify URIs of the tracks
        track_uris = []

        # Iterate over the scraped tracks and search for them on Spotify
        for track, artist in scrapedTracks:
            # Search for the track on Spotify
            results = sp.search(q=f'track:{track} artist:{artist}', type='track')

            # Check if any results were found
            if results['tracks']['items']:
                # Get the URI of the first track in the search results
                track_uri = results['tracks']['items'][0]['uri']
                track_uris.append(track_uri)
                print('******************************************************************\n'
                    f'Added {track} to Spotify Playlist\n'
                    '******************************************************************')
            else:
                print(f'No matching track found on Spotify for: {track} by {artist}')
            
            scraped_count -= 1
            print(f'Total tracks left to add: {scraped_count}.')

            time.sleep(5)

        # Add the tracks to the Spotify playlist
        sp.playlist_add_items(playlist_id, track_uris)
        print('Finished adding tracks to the Spotify playlist.\n'
        '---------------------------------------------------------------------------------------------------')
    except Exception as e:
        print('Error adding tracks to Spotify playlist:', e)

    try:
        #################################################
        # Remove duplicate tracks from Spotify Playlist #
        #################################################
        all_tracks = []

        # Retrieves tracks from Spotify playlist
        playlist = sp.playlist(playlist_id, fields="tracks,next")
        tracks = playlist['tracks']

        # Get each track's name, artist, and ID. 
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
                print (f"Removed duplicate(s) of {track[0]} by {track[1]} from the playlist.")
                time.sleep(5)

        print('---------------------------------------------------------------------------------------------------\n'
              f"Removed {len(duplicate_tracks)} duplicate tracks from the playlist.")
    except Exception as e:
        print('Error removing duplicate tracks from Spotify playlist:', e)

# Call the function with your Spotify playlist ID, client ID, client secret, redirect URI, and scope
add_to_spotify_playlist('0z6CpS8ikzUdmSeD54c4Ts', os.environ['CLIENT_ID'], os.environ['CLIENT_SECRET'], 'http://localhost:8888/callback', 'playlist-modify-public', scraped_count)

print('The script has finished successfully!')