from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import re
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

items = []

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

            if primary_content_div.find('h3', class_='u-mb0' != None) and (primary_content_div.find('div', class_='u-mb1') != None) and (primary_content_div.find_all('div', class_='u-h5') != []):
                track = primary_content_div.find('h3', class_='u-mb0').get_text(strip=True)
                artist = primary_content_div.find('div', class_='u-mb1').get_text(strip=True)
                year = primary_content_div.find_all('div', class_='u-h5')[-1].get_text(strip=True)
                if re.match('^2023', year):
                    items.append((track, artist))
                    print('Appended track and artist to array')

        loop_count += 1
    except Exception as e:
        print('Error:', e)
        break
    

print('The script has finished successfully!')