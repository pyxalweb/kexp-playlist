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

max_loops = 1
loop_count = 0
print(f'We will scrape {max_loops} playlist page(s).')

scrapedTracks = []

while loop_count < max_loops:
    try:
        print('Waiting 5 seconds between playlist page(s).')
        time.sleep(5)

        page_source = driver.page_source
        print('Selenium has the page source.')

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
                    print(f'Appended {track} by {artist} to array.')

        # Click the 'previous' link to go to the next playlist page
        previous_link = driver.find_element(By.ID, "previous")
        previous_link.click()

        # Add 1 to the loop_count
        loop_count += 1
    except Exception as e:
        print('Error:', e)
        break
    
driver.quit()
print('Done scraping!')

print(f'Scraped the following tracks: {scrapedTracks}')

#####################################
# Import tracks to Spotify Playlist #
#####################################
def add_to_spotify_playlist(playlist_id, client_id, client_secret, redirect_uri, scope):
    try:
        # Authenticate with Spotify
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                    client_secret=client_secret,
                                                    redirect_uri=redirect_uri,
                                                    scope=scope))
        print('Successfully authenticated with Spotify.')

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
            else:
                print(f'No matching track found on Spotify for: {track} by {artist}')
            
            # Close the connection after each API request
            sp._session.close()

        # Add the tracks to the Spotify playlist
        sp.playlist_add_items(playlist_id, track_uris)
        print('Tracks added to the Spotify playlist.')
    except Exception as e:
        print('Error adding tracks to Spotify playlist:', e)

# Call the function with your Spotify playlist ID, client ID, client secret, redirect URI, and scope
add_to_spotify_playlist('6l04uhnCMeOjO3R1vLEkHW', os.environ['CLIENT_ID'], os.environ['CLIENT_SECRET'], 'http://127.0.0.1:8080', 'playlist-modify-public')

print('The script has finished successfully!')