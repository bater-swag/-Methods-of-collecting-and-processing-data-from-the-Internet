from bs4 import BeautifulSoup as bs
import requests
import pandas as pd

headers = {
    'User-agent': 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36'}


def ros_potreb(main_link, search_str, type_product, n_str):
    product_info = []
    html = requests.get(
        main_link + '/' + search_str + '/' + type_product + '/',
        headers=headers).text
    parsed_html = bs(html, 'lxml')
    for i in range(n_str):
        products_block = parsed_html.find_all('div', {
            'class': 'wrap-product-catalog__item grid-padding grid-column-4 '
                     'grid-column-large-6 grid-column-middle-12 '
                     'grid-column-small-12 grid-left js-product__item'})
        for product in products_block:
            href = product.find('a', {
                'class': 'block-product-catalog__item js-activate-rate util-hover-shadow clear'})[
                'href']
            name = product.find('div', {'class': 'product__item-link'}).text
            rate = product.find('div',
                                {'class': 'rate green rating-value'}).text
            test = product.find('div', {'class': 'rating-block'})
            values = test.find_all('i', {'class': 'green'})
            value_product = [int(cost['data-width']) for cost in values]
            if len(value_product) < 4:
                value_product.append(None)
            product_info.append(
                [name, value_product[0], value_product[1], value_product[2],
                 value_product[3],
                 rate, main_link + href])
        next_btn_block = parsed_html.find('a', {
            'class': 'page-num page-item last AJAX_toggle'})
        next_btn_link = next_btn_block['data-ajax_href']
        html = requests.get(main_link + next_btn_link, headers=headers).text
        parsed_html = bs(html, 'lxml')

    res_product = pd.DataFrame(data=product_info,
                               columns=['name', 'Безопасность', 'Натуральность',
                                        'Пищевая ценность', 'Качество',
                                        'Общая оценка', 'link'])
    res_product.to_csv(f'res_product.csv')


# type_product = 'molochnie_produkti'
# product = 'moloko'
# n_str = 3
type_product = input("Введите категорию продукта: ")
product = input("Введите тип продукта: ")
n_str = int(input("Введите число страниц: "))
ros_potreb('https://roscontrol.com/category/produkti/', search_str=type_product,
           type_product=product, n_str=n_str)
