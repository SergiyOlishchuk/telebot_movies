from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from time import sleep

from database import DataBase

db = DataBase()

driver = webdriver.Chrome()

driver.get('https://megogo.net/ua/search-extended?category_id=films&main_tab=filters&sort=popular')

print('Page was loaded')
sleep(3)

print('Opening whole page')

while True:
    sleep(1)
    try:
        driver.find_element(By.CLASS_NAME, 'pagination-spinner').click()
        sleep(1.5)
        print('Opened new part')
    except Exception as e:
        print(e)
        break

print('Page was open')

print('Filling DB')

index = 1
elems = driver.find_elements(By.CSS_SELECTOR, '.card.videoItem')
count = len(elems)

for el in elems:
    name = el.get_attribute('title')
    content = el.find_element(By.CSS_SELECTOR, '.card-content.video-content')
    link = content.find_element(By.TAG_NAME, 'a').get_attribute('href')
    info = content.find_element(By.CSS_SELECTOR, '.video-info.card-content-info')
    year = info.find_element(By.CLASS_NAME, 'video-year').text
    genre = info.find_element(By.CLASS_NAME, 'video-country').text
    
    try:
        db.add_movie({'name': name, 'genre' : genre, 'year': int(year), 'link' : link})
    except Exception as e:
        with open(r'C:\Users\User\Desktop\telebot fims\errors.txt', 'a') as file:
            file.write(str(e))
            file.write('\n')
            file.write(name + genre + year + link)
            file.write('\n\n')
    
    print('Movie was added ' + str(index) + '/' + str(count))
    index += 1


driver.close()

print('Program end')