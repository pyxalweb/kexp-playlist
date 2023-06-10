# kexp-playlist

## Infinite New Music Glitch!

This script will visit KEXP's Playlist page and add all Tracks (song name, artist name) that were released in the current year to an array, which is then in turn added to a Spotify Playlist.

If the script runs daily and scrapes the entire days worth (approximately 20 pages) of Tracks, then it should in theory be pretty good at automatically gathering new music. The user can then view the Spotify Playlist on a regular basis and cherry-pick their favorite songs, thus always being on the cutting edge.

## How Does it Work?

The 'https://www.kexp.org/playlist/' page's Playlist content is dynamically generated. This means that we must use the Selenium library to get the HTML markup.

We then use the BeautifulSoup library to parse through the HTML markup and find the appropriate content. Each Track is contained within a div that has a class of '.PlaylistItem-primaryContent'. However the KEXP Playlist also uses this div and class name for other extraneous content such as advertisements, logging air breaks, etc. So we must be very specific in the HTML that we are looking to find. Additionally we only want Tracks that have a publish date of the current year so we use a regular expression to ensure this.

Once the script has finished scraping the page then it will find the 'Earlier' link (pagination for the previous content) which is an anchor link that has an ID of '#previous'. This is clicked and the 'loop_count' is incremented. This will end only when the user defined 'max_loops' is reached.

Next we authenticate with Spotify and prepare to add the Tracks to the user defined Spotify Playlist ID. We're using the SpotifyOAuth class which supports the Spotify API's 'Client Authorization Code Flow' method. We iterate through the scraped Tracks array and use Spotify's 'search' endpoint to see if the Track exists on Spotify, if it does then we append that Track URI to our new 'track-uris' array. Then finally we add that Track to the Spotify Playlist.

Lastly we want to remove any duplicate Tracks. Maybe eventually I'll modify the script to check for an existing Track before it adds it, but for now this is fine. The script will retrieve all of the Tracks from the Spotify Playlist and then loop through each one, checking if the Track exists more than once. If it does, then remove all instances of the Track. Then add the Track again.

## Todo:

* Currently the script does not check if the Track already exists in the Playlist or not. After it finishes adding all Tracks, then it checks for and removes any duplicates. It does this by removing all Tracks that occur more than once, and then adds one instance of the Track back again. This is a waste of resources. A better solution would be to check if the Track exists in the Playlist before it adds it, if it exists then it is skipped and if it does not exist then it adds it.