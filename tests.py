from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from time import sleep

driver = webdriver.Chrome()

driver.get('https://megogo.net/ua/search-extended?category_id=films&main_tab=filters&sort=popular')

print('Page was loaded')
sleep(3)

# pagination_spinner = driver.find_element(By.CLASS_NAME, 'pagination-spinner')
# print(pagination_spinner)

print('Opening whole page')
while True:
    try:
        pagination_spinner = driver.find_element(By.CLASS_NAME, 'pagination-spinner').click()
        sleep(1)
        print('Opened new part')
    except:
        break

print('Page was open')

driver.find_element(By.CSS_SELECTOR, 'body').send_keys(Keys.END)

input()

driver.close()

print('Program end')