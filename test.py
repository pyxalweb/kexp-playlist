from selenium import webdriver
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