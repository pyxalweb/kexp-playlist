from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import os
import csv
import time
import datetime

# Create a new instance of the Firefox driver
driver = webdriver.Firefox()

# Navigate to the URL
driver.get('https://www.kexp.org/playlist/')

# How many pages to scrape
max_loops = 1

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

# Create a CSV file
# 'with' statement will automatically close the file when done
# 'open' returns a file object, which is assigned to the variable 'csvfile'
# 'w' parameter indicates that we are writing to the file
# 'newline' parameter is required to avoid blank lines between rows
with open(csv_file_path, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Title', 'Artist'])
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
                # Check if the playlist item has a song title and artist name
                # If it does not, then skip it
                if primary_content_div.find('h3', class_='u-mb0' != None) and (primary_content_div.find('div', class_='u-mb1') != None):
                    title = primary_content_div.find('h3', class_='u-mb0').get_text(strip=True)
                    artist = primary_content_div.find('div', class_='u-mb1').get_text(strip=True)
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
# Create a list to store all the rows from the CSV files
all_rows = []

# Loop through all the files in the outputs directory
for filename in os.listdir(outputs_dir):
    if filename.endswith(".csv") and filename != "combined.csv":  # Skip "combined.csv" file
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

print('Done!')