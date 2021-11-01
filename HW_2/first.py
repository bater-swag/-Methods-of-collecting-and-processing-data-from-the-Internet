from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
import time
import re
from pymongo import MongoClient
import random

headers = {
    'User-agent': 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36'}


def hh(main_link, search_str, n_str):
    hh_data = []
    # n_str - кол-во просматриваемых страниц
    html = requests.get(
        main_link + '/search/vacancy?clusters=true&enable_snippets=true&text=' + search_str + '&showClusters=true',
        headers=headers).text
    parsed_html = bs(html, 'lxml')
    for i in range(n_str):
        jobs_block = parsed_html.find('div', {'class': 'vacancy-serp'})
        jobs_list = jobs_block.findChildren(recursive=False)
        for job in jobs_list:
            req = job.find('span', {'class': 'g-user-content'})
            if req != None:
                main_info = req.findChild()
                job_name = main_info.getText()
                job_link = main_info['href']
                salary = job.find('div',
                                  {'class': 'vacancy-serp-item__compensation'})
                if not salary:
                    salary_min = None
                    salary_max = None
                else:
                    salary = salary.getText().replace(u'\xa0', u'')
                    salaries = salary.split('-')
                    salaries[0] = re.sub(r'[^0-9]', '', salaries[0])
                    salary_min = int(salaries[0])
                    if len(salaries) > 1:
                        salaries[1] = re.sub(r'[^0-9]', '', salaries[1])
                        salary_max = int(salaries[1])
                    else:
                        salary_max = None
                hh_data.append(
                    [job_name, main_link + job_link, salary_min,
                     salary_max,
                     main_link])
            time.sleep(random.randint(1, 3))
            next_btn_block = parsed_html.find('a', {
                'data-qa': 'pager-next'})
            next_btn_link = next_btn_block['href']
            html = requests.get(main_link + next_btn_link, headers=headers).text
            parsed_html = bs(html, 'lxml')

    res_hh = pd.DataFrame(data=hh_data,
                          columns=['title', 'href', 'salary_min',
                                   'salary_max', 'link'])
    res_hh.to_csv(f'res_hh.csv')


def superjob(main_link, search_str, n_str):
    superjobs_data = []
    # n_str - кол-во просматриваемых страниц
    base_url = main_link + '/vacancy/search/?keywords=' + search_str + '&geo%5Bc%5D%5B0%5D=1'
    session = requests.Session()
    for i in range(n_str):
        request = session.get(base_url, headers=headers)
        if request.status_code == 200:
            soup = bs(request.content, 'lxml')
            divs = soup.find_all('div', {
                'class': 'f-test-search-result-item'})
            for div in divs:
                try:
                    main = div.find('span',
                                    {'class': '_185V- _1_rZy _2ogzo'})
                    title = main.text
                    href = main.find('a')['href']
                    salary = div.find('span', {
                        'class': '_1OuF_ _1qw9T f-test-text-company-item-salary'}).text
                    salary = salary.replace(u'\xa0', u'')
                    if '—' in salary:
                        salary_min = salary.split('—')[0]
                        salary_min = re.sub(r'[^0-9]', '', salary_min)
                        salary_max = salary.split('—')[1]
                        salary_max = re.sub(r'[^0-9]', '', salary_max)
                        salary_min = int(salary_min)
                        salary_max = int(salary_max)
                    elif 'от' in salary:
                        salary_min = salary[2:]
                        salary_min = re.sub(r'[^0-9]', '', salary_min)
                        salary_min = int(salary_min)
                        salary_max = None
                    elif 'договорённости' in salary:
                        salary_min = None
                        salary_max = None
                    elif 'до' in salary:
                        salary_min = None
                        salary_max = salary[2:]
                        salary_max = re.sub(r'[^0-9]', '', salary_max)
                        salary_max = int(salary_max)
                    else:
                        salary_min = int(re.sub(r'[^0-9]', '', salary))
                        salary_max = int(re.sub(r'[^0-9]', '', salary))

                    superjobs_data.append(
                        [title, 'https://www.superjob.ru' + href,
                         salary_min,
                         salary_max,
                         main_link])
                except AttributeError:
                    continue
            time.sleep(random.randint(1, 10))
            button_next = soup.find('a', {'rel': 'next'})
            res = button_next["href"]
            base_url = main_link + res
        else:
            print('Ошибка')

    res_superjobs = pd.DataFrame(data=superjobs_data,
                                 columns=['title', 'href', 'salary_min',
                                          'salary_max', 'link'])
    res_superjobs.to_csv(f'res_superjobs.csv')


search_str = 'Developer'
n_str = 1

hh('https://belgorod.hh.ru', search_str, n_str)
superjob('https://russia.superjob.ru/', search_str, n_str)
