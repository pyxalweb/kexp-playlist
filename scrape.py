from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import csv
import time

# Create a new instance of the Firefox driver
driver = webdriver.Firefox()

# Navigate to the URL
driver.get('https://www.kexp.org/playlist/')

# How many pages to scrape
max_loops = 3

# Always start at 0
loop_count = 0

# Create a CSV file
# 'with' statement will automatically close the file when done
# 'open' returns a file object, which is assigned to the variable 'csvfile'
# 'w' parameter indicates that we are writing to the file
# 'newline' parameter is required to avoid blank lines between rows
with open('output.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Title', 'Content'])
    print('Created CSV file')

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
                # Check if the playlist item has a title and content
                # If the playlist item does not have a title and content, skip it
                if primary_content_div.find('h3', class_='u-mb0' != None) and (primary_content_div.find('div', class_='u-mb1') != None):
                    title = primary_content_div.find('h3', class_='u-mb0').get_text(strip=True)
                    content = primary_content_div.find('div', class_='u-mb1').get_text(strip=True)
                writer.writerow([title, content])
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

print('Done!')