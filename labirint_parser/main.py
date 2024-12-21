import requests
from bs4 import BeautifulSoup
import csv

CSV = 'cards.csv'
HOST = 'https://www.labirint.ru'
URL = 'https://www.labirint.ru/books/'
# создаю перемнную которая будет в себе хранить данные - заголовки(accept, headers)
HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
              'application/signed-exchange;v=b3;q=0.7',
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile '
                  'Safari/537.36',
}
 

def get_html(url: str, params=''):
    r = requests.get(url, headers=HEADERS, params=params)
    return r


def get_content(html) -> list[dict]:
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='js-content-block-tab js-content-block-tab_all content-block')
    # Инициализируем пустой список для хранения всех найденных продуктов
    products = []

    # Проходим по каждому блоку контента и находим продукты внутри них
    for block in items:
        products.extend(block.find_all('div', class_='product need-watch'))
    cards: list = []

    for item in products:
        link_product = HOST + item.find('div', class_='product-cover').find('a').get('href')

        # Получаем дополнительные данные со страницы продукта
        additional_data = get_additional_data(link_product)

        cards.append(
            {
                'title': item.find('div', class_='product-cover').find('a').get('title'),
                'price_with_discount': item.get('data-discount-price'),
                'price': item.get('data-price'),
                'link-product': link_product,
                **additional_data
            }
        )
    return cards


# Функция для получения дополнительных данных с новой страницы
def get_additional_data(url: str) -> dict:
    html = get_html(url).text
    soup = BeautifulSoup(html, 'html.parser')
    # Для примера будем парсить описание (если оно есть)
    description_tag = soup.find('div',id='product-about').find('p')
    description = description_tag.get_text(strip=True) if description_tag else 'No description'

    return {
        'description': description,
    }



def save_doc(items, path):
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')  # ; легко читает excel. таким образом можно легко читать csv файла через excel
        writer.writerow(['Название', 'цена со скидкой', "цена без скидки", "ссылка на книгу", "описание"])
        for item in items:
            writer.writerow([item['title'], item['price_with_discount'], item['price'], item['link-product'], item['description']])


def parser():
    PAGGENATION = int(input('укажите кол-во страниц для парсинга').strip())
    html = get_html(URL)
    if html.status_code == 200:
        cards: list = []
        for page in range(1, PAGGENATION + 1):
            print(f'парсим страницу {page}')
            html = get_html(url=URL, params={'page': page})
            cards.extend(get_content(html.text))
            save_doc(cards, CSV)
    else:
        print('Error')

parser()
