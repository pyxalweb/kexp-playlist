from selenium import webdriver
from bs4 import BeautifulSoup
print('1. successfully ran')

from selenium.webdriver.chrome.options import Options
print('2. successfully ran')

options = Options()
print('3. successfully ran')

options.add_argument("--headless")
print('4. successfully ran')

driver = webdriver.Chrome(options=options)
print('5. successfully ran')

driver.get('https://www.kexp.org/playlist/')
print('6. successfully ran')

page_source = driver.page_source
print('Page source is now available')

soup = BeautifulSoup(page_source, 'html.parser')
print('Parsed page source with BeautifulSoup')