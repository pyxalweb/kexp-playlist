# kexp-playlist
Get a list of the most recent KEXP playlist in CSV format

The script uses Selenium to open a browser window because the KEXP playlist is generated using Javascript and so we must wait for that to be populated within the DOM.

Once the browser is open, the script will create a CSV file within the same directory that the Terminal is currently in.

The while loop will begin and run for as many loops as desired by the user. Each time it runs it will wait for a default of 5 seconds so that we do not overburden or abuse the KEXP web server.

As mentioned above, the playlist data is populated by Javascript on the KEXP web page. So we must wait for Selenium to get the completed page source. Once it does then BeautifulSoup will be able to parse the playlist data which is contained within a div that has an id of 'playlist-plays'.

For each playlist item, the script will check that it contains an h3 with a class of 'u-mb0' which represents the song title and that it contains a div with a class of 'u-mb1' which represents the artist name. If both of these elements exist, then it will write the song title and artist name to the CSV file. If these elements do not exist then it will skip the playlist item because it is not the desired data we want; ex: air breaks, advertisements, or other content that KEXP sometimes displays in the 'playlist-plays' div.

Once all of the items within the 'playlist-plays' div have been looped through then the script will look for a link at the bottom of the page that has an id of 'previous'. This clicks the 'Earlier' pagination link so that it can begin to loop through another page's 'playlist-plays' div. It will do this as many times as desired by the user in the 'max_loops' variable.
