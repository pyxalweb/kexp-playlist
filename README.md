# kexp-playlist
Get a list of the most recent KEXP playlist in CSV format and then add the songs to a Spotify Playlist. Currently this is configured to only get the songs that are from the current year (2023) so that we can have a playlist of new music that KEXP is playing. A great tool for finding new music! Here is a link to the playlist:
[https://open.spotify.com/playlist/0z6CpS8ikzUdmSeD54c4Ts?si=f63c5bc185704eeb](https://open.spotify.com/playlist/0z6CpS8ikzUdmSeD54c4Ts?si=f63c5bc185704eeb)

The script cannot be headless (to my knowledge) and must use Selenium to open a browser window because the KEXP playlist is generated using Javascript and so we must wait for that to be populated within the DOM.

Once the browser is open, the script will create a CSV file within the 'outputs' directory with a filename that is set to the current date and time.

The while loop will begin and run for as many loops as desired by the user. Each time it runs it will wait for a default of 5 seconds so that we do not overburden or abuse the KEXP web server.

As mentioned above, the playlist data is populated by Javascript on the KEXP web page. So we must wait for Selenium to get the completed page source. Once it does then BeautifulSoup will be able to parse the playlist data which is contained within a div that has an id of 'playlist-plays'.

For each playlist item, the script will check that it contains the following:
- An h3 with a class of 'u-mb0' which represents the song title.
- A div with a class of 'u-mb1' which represents the artist name.
- A div with a class of 'u-h5' which represnts the publish year. NOTE: There are two divs with a class of 'u-h5' and we must get the last one only. We get the year because currently the script is configured to only get songs from X year as I am using this script to generate a playlist of songs that KEXP plays that are (new) from the current year. In the future this will be optional.
If these elements exist, then it will write the song title and artist name to the CSV file. If these elements do not exist then it will skip the playlist item because it is not the desired data we want; ex: air breaks, advertisements, or other content that KEXP sometimes displays in the 'playlist-plays' div.

Once all of the items within the 'playlist-plays' div have been looped through then the script will look for a link at the bottom of the page that has an id of 'previous'. This clicks the 'Earlier' pagination link so that it can begin to loop through another page's 'playlist-plays' div. It will do this as many times as desired by the user in the 'max_loops' variable.

Finally the script will connect to the Spotify API via your playlist_id, client_id, and client_secret. All of which can be acquired by creating a Spotigy Developer account. It will then loop through the 'combined.csv' file found in the 'csv_file_path' location on your machine. It will then attempt to add each song from the CSV to a Spotify Playlist of your choice, waiting 5 seconds between each attempt so that we do not overburden or abuse the Spotify API.

## Todo:
TODO: Write a cron job to automatically run this python script at a specific time of day.

TODO: Figure out what is causing the following errors to be printed to terminal when adding songs to the Spotify playlist. It seems to be a permissions issue. It's important to note however that the script is successfully adding the songs to the playlist despite these errors.
"Couldn't write token to cache at: .cache"
"Couldn't read cache at: .cache"

TODO: Modify the script so that scraping songs from a specific year can easily be toggled on/off so that we can easily switch between scraping all songs or by year -- without having to manually edit the code.