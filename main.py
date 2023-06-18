"""
Script Name: KEXP to Spotify by Year
Author: Alex Winter
Version: 1.0
Description: This script will visit KEXP's Playlist page and add all Tracks (song name, artist name) that were released in the current year to an array, which is then in turn added to a Spotify Playlist. If the script runs daily and scrapes the entire day's worth (approximately 20 pages) of Tracks, then it should in theory be pretty good at automatically gathering new music. The user can then manually view the Spotify Playlist on a regular basis and cherry-pick their favorite songs, thus always being on the cutting edge.

Usage:
    - Run the script with Python 3.x
    - Dependencies: selenium, beautifulsoup4, spotipy, colorama
    - Set the max_loops variable to determine how many Playlist pages to scrape (ex: 20)
    - Set the year (ex: 2023)
    - Set your Spotify playlist ID (this can be found in the URL of your Spotify Playlist)
    - Set your client ID, client secret (this can be generated at developer.spotify.com)

Author's Note: Please consider donating to KEXP as they are a non-commercial radio station and a non-profit entity that can only function with your support. I understand that Spotify is in some ways the antithesis to KEXP. However it is a useful tool that allows me to easily organize and arrange music playlists. This script was created for fun and there is no intention otherwise.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import re
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import colorama

# use the following if running in a cron job script:
os.environ['DISPLAY'] = ':0'

# use the following on 32-Bit ARM Raspberry Pi only:
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver import Chrome

print('Dependencies imported successfully')

# run Chrome/Chromium as a headless browser
options = Options()
options.add_argument('--headless')

# comment out the following on 32-Bit ARM Raspberry Pi only:
driver = webdriver.Chrome(options=options)

# use the following on 32-Bit ARM Raspberry Pi only:
# service = Service('/usr/lib/chromium-browser/chromedriver')
# driver = Chrome(service=service, options=options)

print('Chrome WebDriver is ready')

driver.get('https://www.kexp.org/playlist/')
print('Selenium has the URL ready')

colorama.init()

max_loops = 3
loop_count = 1
print(f'Scraping {max_loops} playlist page(s)')

scraped_count = 0

scraped_tracks = []

# loop through each KEXP Playlist page
while loop_count <= max_loops:
    try:
        print(colorama.Fore.MAGENTA + f'Page {loop_count} of {max_loops}.'  + colorama.Style.RESET_ALL)

        page_source = driver.page_source
        print('Selenium has the page source')

        soup = BeautifulSoup(page_source, 'html.parser')
        print('BeautifulSoup has parsed the HTML')

        # Find the parent div and child divs
        parent_div = soup.find('div', id='playlist-plays')
        playlist_items = parent_div.find_all('div', class_='PlaylistItem')
        print('Found playlist items')

        tracks_per_page_count = 0

        # Loop through the child divs
        for playlist_item in playlist_items:
            # Find the div which contains the track name, artist name, and year
            primary_content_div = playlist_item.find('div', class_='PlaylistItem-primaryContent')

            # If the 'PlaylistItem-primaryContent' div does not contain the appropriate text (track name, artist name, year) then it is likely a sponsor, air break, etc and should be skipped
            if primary_content_div.find('h3', class_='u-mb0' != None) and (primary_content_div.find('div', class_='u-mb1') != None) and (primary_content_div.find_all('div', class_='u-h5') != []):
                # Get the track name, artist name, and year
                track = primary_content_div.find('h3', class_='u-mb0').get_text(strip=True)
                artist = primary_content_div.find('div', class_='u-mb1').get_text(strip=True)
                year = primary_content_div.find_all('div', class_='u-h5')[-1].get_text(strip=True)
                # If the year is matched, then proceed
                if re.match('^2023', year):
                    # Add it to the array
                    scraped_tracks.append((track, artist))
                    scraped_count += 1
                    tracks_per_page_count += 1
                    print(colorama.Fore.GREEN + f'{track} by {artist} added to array' + colorama.Style.RESET_ALL)

        if tracks_per_page_count == 0:
            print (colorama.Fore.RED + 'None of the playlist items were tracks from 2023' + colorama.Style.RESET_ALL)

        print(colorama.Fore.CYAN + f'Total tracks scraped: {scraped_count}.' + colorama.Style.RESET_ALL)

        # Click the 'previous' link to go to the next playlist page
        previous_link = driver.find_element(By.ID, 'previous')
        previous_link.click()

        # Add 1 to the loop_count
        loop_count += 1

        time.sleep(5)
    except Exception as e:
        print('Error:', e)
        break
    
driver.quit()

print('Finished scraping tracks from KEXP Playlist page(s)')

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

        print('Successfully authenticated with Spotify')
    except Exception as e:
        print('Error authenticating with Spotify:', e)

    try:
        #####################################
        # Import tracks to Spotify Playlist #
        #####################################
        added_count = 1

        # Create a list to store the Spotify URIs of the tracks
        track_uris = []

        # Iterate over the scraped tracks and search for them on Spotify
        for track, artist in scraped_tracks:
            # Search for the track on Spotify
            results = sp.search(q=f'track:{track} artist:{artist}', type='track')

            # Check if any results were found
            if results['tracks']['items']:
                # Get the URI of the first track in the search results
                track_uri = results['tracks']['items'][0]['uri']
                track_uris.append(track_uri)
                print(colorama.Fore.GREEN + f'{track} by {artist} added to Spotify Playlist' + colorama.Style.RESET_ALL)
            else:
                print(colorama.Fore.RED + f'No matching track found on Spotify for: {track} by {artist}' + colorama.Style.RESET_ALL)
            
            print(colorama.Fore.CYAN + f'{added_count} of {scraped_count}' + colorama.Style.RESET_ALL)
            added_count += 1

            time.sleep(5)

        # Add the tracks to the Spotify playlist
        sp.playlist_add_items(playlist_id, track_uris)
        print('Finished adding tracks to the Spotify playlist')
    except Exception as e:
        print('Error adding tracks to Spotify playlist:', e)

    try:
        #################################################
        # Remove duplicate tracks from Spotify Playlist #
        #################################################
        all_tracks = []

        # Retrieves tracks from Spotify playlist
        playlist = sp.playlist(playlist_id, fields='tracks,next')
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
                print (colorama.Fore.YELLOW + f'{track[0]} by {track[1]} duplicate tracks removed from Spotify Playlist' + colorama.Style.RESET_ALL)
                time.sleep(5)

        print(colorama.Fore.CYAN + f'{len(duplicate_tracks)} duplicate tracks removed from Spotify Playlist' + colorama.Style.RESET_ALL)
    except Exception as e:
        print('Error removing duplicate tracks from Spotify playlist:', e)

# Call the function with your Spotify playlist ID, client ID, client secret, redirect URI, and scope
add_to_spotify_playlist('0z6CpS8ikzUdmSeD54c4Ts', os.environ['CLIENT_ID'], os.environ['CLIENT_SECRET'], 'http://localhost:8888/callback', 'playlist-modify-public', scraped_count)

print('The script has successfully finished!')
colorama.deinit()