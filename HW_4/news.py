from lxml import html
import requests
from datetime import datetime
from pymongo import MongoClient

headers = {
    'User-agent': 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36'}
date_format = '%Y-%m-%dT%H:%M:%S%z'
keys = ('title', 'date', 'link')


def take_requests(url):
    request = requests.get(url=url)
    main = html.fromstring(request.text)
    return main


def take_date(url):
    main = take_requests(url)
    url_source = main.xpath('//h1[@class="mg-story__title"]/a/@href')
    main_source = take_requests(url_source[0])
    date = main_source.xpath('//time[@itemprop="datePublished"]/@datetime')
    return date


def prepare_format_date(date):
    new_date = datetime.strptime(date, date_format)
    return new_date


def append_to_dict(news, text, news_date, news_links, source):
    news_dict = {}
    for key, value in zip(keys, [text, news_date, news_links]):
        news_dict[key] = value
    news_dict['source'] = source
    news.append(news_dict)
    return news


def get_news_yandex_ru():
    news = []

    link_lenta = 'https://yandex.ru/news'

    request = requests.get(url=link_lenta, headers=headers)
    root = html.fromstring(request.text)

    root.make_links_absolute(link_lenta)
    class_names = ['mg-grid__col mg-grid__col_xs_4', 'mg-grid__col mg-grid__col_xs_6']
    for class_name in class_names:
        res = root.find_class(class_name)
        for i in res:
            link = i.xpath('.//div[@class="mg-card__text-content"]//div[@class="mg-card__text"]/a/@href')
            text = i.xpath('.//div[@class="mg-card__text-content"]//div[@class="mg-card__text"]/a/h2/text()')
            if text == [] or link == []:
                continue
            else:
                text = text[0].replace(u'\xa0', u' ')
                source = i.xpath(
                    './/div[@class="mg-card-footer mg-card__footer mg-card__footer_type_image"]'
                    '//span[@class="mg-card-source__source"]/a/@aria-label')[0].split(': ')[1]
                time = i.xpath(
                    './/div[@class="mg-card-footer mg-card__footer mg-card__footer_type_image"]'
                    '//span[@class="mg-card-source__time"]/text()')
                date = prepare_format_date(take_date(link[0])[0])
                append_to_dict(news, text, date, link, source)
    load_to_base('news', 'news_parser_db')
    return news


def get_news_lenta():
    news_dict = []
    link_lenta = 'https://lenta.ru/'
    request = requests.get(url=link_lenta, headers=headers)
    root = html.fromstring(request.text)
    all_news = root.xpath('//div[@data-partslug="text"]')
    for news in all_news:
        name_news = news.xpath('./a/span/text()')
        link = news.xpath('./a/@href')
        if name_news != []:
            name_news = name_news[0].replace(u'\xa0', u' ')
            link = link_lenta + f'{link[0]}'
            main_source = take_requests(url=link)
            date = main_source.xpath('//time[@class="g-date"]/@datetime')
            if date != []:
                new_date = prepare_format_date(date[0])
                append_to_dict(news_dict, name_news, new_date, link, source='lenta.ru')
            else:
                continue
        else:
            continue
    load_to_base('news', 'news_parser_db')
    return news_dict


def load_to_base(db_name, collection_name, news_list):
    mongodb_uri = 'mongodb://172.17.0.2:27017/'
    mongodb = MongoClient(mongodb_uri)
    db = mongodb[db_name]
    collection = db[collection_name]
    for news in news_list:
        collection.insert_one(news)
