from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
print('Dependencies imported successfully.')

options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)
print('Chrome WebDriver is ready.')

driver.get('https://www.kexp.org/playlist/')
page_source = driver.page_source
print('Selenium has the page source.')

soup = BeautifulSoup(page_source, 'html.parser')
print('BeautifulSoup has parsed the HTML.')

print('The script has finished successfully!')

max_loops = 1
loop_count = 0
print(f'We will scrape {max_loops} playlist page(s).')