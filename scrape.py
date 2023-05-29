from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import os
import csv
import time
import datetime
import re
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Create a new instance of the Firefox driver
driver = webdriver.Firefox()

# Navigate to the URL
driver.get('https://www.kexp.org/playlist/')

# How many pages to scrape
max_loops = 25

# Always start at 0
loop_count = 0

# Get the current date and time
now = datetime.datetime.now()
formatted_date_time = now.strftime("%Y-%m-%d_%H-%M-%S")
print(formatted_date_time)

# Get the directory of the script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Create an 'outputs' directory if it doesn't exist
outputs_dir = os.path.join(script_dir, "outputs")
if not os.path.exists(outputs_dir):
    os.makedirs(outputs_dir)

# Create the CSV file name and path
csv_file_path = os.path.join(outputs_dir, 'output_' + formatted_date_time + '.csv')

###################################
# Create the 'output' CSV file    #
###################################
# 'with' statement will automatically close the file when done
# 'open' returns a file object, which is assigned to the variable 'csvfile'
# 'w' parameter indicates that we are writing to the file
# 'newline' parameter is required to avoid blank lines between rows
with open(csv_file_path, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Title', 'Artist'])
    print('Created CSV file')

    ###################################
    # Scrape the KEXP playlist        #
    ###################################
    while loop_count < max_loops:
        try:
            # Wait X seconds between each page
            print('Waiting 5 seconds')
            time.sleep(5)
        
            # Get the dynamically generated content using Selenium
            page_source = driver.page_source
            print('Page source is now available')

            # Parse the page source with BeautifulSoup
            soup = BeautifulSoup(page_source, 'html.parser')
            print('Parsed page source with BeautifulSoup')

            # Find the parent div and extract the playlist items
            parent_div = soup.find('div', id='playlist-plays')
            playlist_items = parent_div.find_all('div', class_='PlaylistItem')
            print('Found playlist items!')

            # Write the playlist items to the CSV file
            for playlist_item in playlist_items:
                primary_content_div = playlist_item.find('div', class_='PlaylistItem-primaryContent')
                # Check if the playlist item has a song title, artist name, and year
                # If it does not, then skip it
                # We use 'find_all' because playlist items have multiple 'u-h5' divs and we only want the last one                
                if primary_content_div.find('h3', class_='u-mb0' != None) and (primary_content_div.find('div', class_='u-mb1') != None) and (primary_content_div.find_all('div', class_='u-h5') != []):
                    title = primary_content_div.find('h3', class_='u-mb0').get_text(strip=True)
                    artist = primary_content_div.find('div', class_='u-mb1').get_text(strip=True)
                    year = primary_content_div.find_all('div', class_='u-h5')[-1].get_text(strip=True)
                    if re.match('^2023', year):
                        writer.writerow([title, artist])
                        print('Wrote playlist item to CSV file')

            # Click the 'previous' link
            previous_link = driver.find_element(By.ID, "previous")
            previous_link.click()
            loop_count += 1
            print('Continuing to next page. Loop count:', loop_count)
        except Exception as e:
            print("Error:", e)
            break

# Close the browser
driver.quit()

print('Done scraping!')

###################################
# Combine CSV files into one file #
###################################
# Get a list of files in the outputs directory in descending alphabetical order
files = sorted(os.listdir(outputs_dir), reverse=True)

# Create a list to store all the rows from the CSV files
all_rows = []

# Loop through all the files in the outputs directory
for filename in files:
    if filename.endswith(".csv") and filename != "combined.csv":
        file_path = os.path.join(outputs_dir, filename)
        # Open the CSV file and read its contents
        with open(file_path, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            # Skip the header row
            next(reader)
            # Append all rows to the list of all rows
            for row in reader:
                if row not in all_rows:
                    all_rows.append(row)

# Create the combined CSV file
combined_csv_file_path = os.path.join(outputs_dir, 'combined.csv')
with open(combined_csv_file_path, 'w', newline='') as combined_csvfile:
    writer = csv.writer(combined_csvfile)
    writer.writerow(['Title', 'Artist'])
    # Write all rows to the combined CSV file
    writer.writerows(all_rows)

print('Combined CSV files into', combined_csv_file_path)

#############################################
# Import songs from CSV to Spotify Playlist #
#############################################
def add_to_spotify_playlist(playlist_id, csv_file_path, client_id, client_secret, redirect_uri, scope):
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                   client_secret=client_secret,
                                                   redirect_uri=redirect_uri,
                                                   scope=scope))

    # Read the CSV file and store all rows in a list
    all_rows = []
    with open(csv_file_path, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            if row not in all_rows:
                all_rows.append(row)
    # print(f'All rows: {all_rows}')

    # Get the current songs in the playlist
    current_songs = []
    playlist = sp.playlist(playlist_id, fields="tracks,next")
    tracks = playlist['tracks']
    while tracks:
        for item in tracks['items']:
            current_songs.append((item['track']['name'], item['track']['artists'][0]['name']))
        tracks = sp.next(tracks)
    # print(f'Current songs: {current_songs}')


    # Add songs to the playlist, checking for duplicates
    songs_added = 0
    for row in all_rows:
        title, artist = row[0], row[1]
        if (title, artist) not in current_songs:
            query = f'track:{title} artist:{artist}'
            results = sp.search(q=query, type='track', limit=1)
            if results['tracks']['items']:
                track_id = results['tracks']['items'][0]['id']
                # Wait X seconds between adding each song
                print('Waiting 5 seconds')
                time.sleep(5)
                # Add the song to the playlist
                sp.playlist_add_items(playlist_id, [track_id])
                songs_added += 1
                print(f'Added {title} by {artist} to playlist')

    print(f'Songs added to playlist: {songs_added}')

add_to_spotify_playlist('6l04uhnCMeOjO3R1vLEkHW', combined_csv_file_path, 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX', 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX', 'http://127.0.0.1:8080', 'playlist-modify-public')

print('Done!')
