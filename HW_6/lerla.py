import time
import urllib
import os
from selenium import webdriver
from pymongo import MongoClient
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common import exceptions

driver = webdriver.Chrome()
keys = ('title', 'date', 'link')
items_all = []


def open_url(category):
    url = f'https://leroymerlin.ru/catalogue/{category}/'
    driver.get(url)


def take_information(category):
    all_items = driver.find_elements_by_xpath("//div[@class='phytpj4_plp largeCard']")
    time.sleep(4)
    for item in all_items:
        name = item.find_element_by_xpath('./div/a/span/span').text
        link = item.find_element_by_xpath('./a').get_attribute('href')
        price = int(item.find_element_by_xpath('.//div[@data-qa="product-primary-price"]/p').text.replace(u' ', u''))
        append_to_dict(link, name, price)
        open_product(link, name, category)


def append_to_dict(link, name, price):
    news_dict = {}
    for key, value in zip(keys, [link, name, price]):
        news_dict[key] = value
    items_all.append(news_dict)


def open_product(link, name, category):
    count_img = 0
    create_folder(name, category)

    driver.execute_script("window.open('%s', '_blank')" % link)
    driver.switch_to.window(driver.window_handles[-1])

    media_content = driver.find_element_by_tag_name('uc-pdp-media-carousel')
    imgs = media_content.find_elements_by_xpath('./img')
    for img in imgs:
        src = img.get_attribute('src')
        urllib.request.urlretrieve(src, f'./{category}/{name}/{count_img}.jpg')
        count_img += 1
    parent_handle = driver.window_handles[0]
    driver.switch_to.window(driver.window_handles[-1])
    driver.close()
    driver.switch_to.window(parent_handle)
    time.sleep(1)


def create_folder(name, category):
    if os.path.exists(f'./{category}/{name}'):
        return False
    else:
        os.mkdir(f'./{category}/{name}')


def open_all_pages(category):
    open_url(category)
    os.mkdir(f'{category}')
    next_button = True
    while next_button:
        take_information(category)
        try:
            driver.find_element_by_xpath('//a[@data-qa-pagination-item="right"]').click()
            time.sleep(1)
        except exceptions.NoSuchElementException or exceptions.ElementClickInterceptedException:
            next_button = False

    driver.quit()


open_all_pages(category='dekorativnye-oboi')
