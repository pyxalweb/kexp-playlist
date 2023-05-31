from selenium import webdriver
print('1. successfully ran: from selenium import webdriver')

driver = webdriver.Chrome()
print('2. successfully ran: driver = webdriver.Chrome()')

driver.get('https://www.kexp.org/playlist/')
print('3. successfully ran: driver.get(https://www.kexp.org/playlist/)')
