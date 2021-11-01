from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
import time
import re
from pymongo import MongoClient
import random

headers = {
    'User-agent': 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36'}


def ros_potreb(main_link, search_str, type_product, n_str):
    html = requests.get(
        main_link + '/' + search_str + '/' + type_product + '/',
        headers=headers).text
    parsed_html = bs(html, 'lxml')
    for i in range(n_str):
        jobs_block = parsed_html.find_all('div', {
            'class': 'product__item-leftblock group'})
        for job in jobs_block:
            name = job.find('div', {'class': 'product__item-link'}).text
            rate = job.find('div', {
                'class': 'rate green rating-value'}).text



type_product = 'molochnie_produkti'
product = 'moloko'
n_str = 1

ros_potreb('https://roscontrol.com/category/produkti/', search_str=type_product,
           type_product=product, n_str=n_str)
