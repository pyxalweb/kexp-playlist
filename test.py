from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
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

while loop_count < max_loops:
    try:
        print('Waiting 5 seconds between playlist page(s)')
        time.sleep(5)

        page_source = driver.page_source
        print('Selenium has the page source.')

        soup = BeautifulSoup(page_source, 'html.parser')
        print('BeautifulSoup has parsed the HTML.')

        loop_count += 1
    except Exception as e:
        print('Error:', e)
        break
    

print('The script has finished successfully!')