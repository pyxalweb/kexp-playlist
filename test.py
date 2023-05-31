from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

driver.get('https://www.kexp.org/playlist/')
page_source = driver.page_source
soup = BeautifulSoup(page_source, 'html.parser')
