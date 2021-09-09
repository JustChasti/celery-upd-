import requests

from bs4 import BeautifulSoup
from loguru import logger


headers = {'Content-type': 'application/json', 'Accept': 'text/plain',
           'Content-Encoding': 'utf-8'}


def parse_wb(URL):
    parsed = {}
    parsed['url'] = URL
    urlm = (URL.split('/'))
    urlm = urlm[:5]
    parsed["Art"] = urlm[4]
    URL = ''
    for i in urlm:
        URL += i + '/'
    URL += 'otzyvy'
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    items = soup.find('div', {"class": "main__container"})
    name = items.find('meta', {"itemprop": "name"})
    parsed['Name'] = name['content']

    item = items.find('div', {"class": "same-part-kt__common-info"})
    otz = item.find('span', {"data-link": "{include tmpl='productCardCommentsCount'}"}).text
    k_otz = ''
    for symb in otz:
        if symb >= '0' and symb <= '9':
            k_otz = k_otz + symb
    parsed['Col_otz'] = k_otz
    parsed['rating'] = item.find('span', {"data-link": "text{: productCard^star}"}).text

    parsed['description'] = items.find('p', {"data-link": "text{:productCard.description}"}).text.replace(u'\n', u' ')

    # properties
    properties = items.find('table', {"class": "product-params__table"})
    params = properties.find_all('span', {"class": "product-params__cell-decor"})
    cells = properties.find_all('td', {"class": "product-params__cell"})
    properties = {}
    for i in range(len(cells)):
        properties[params[i].find('span').text] = cells[i].text
    parsed['properties'] = properties

    price = items.find('span', {"class": "price-block__final-price"})
    if price is not None:
        price = price.text
        final_price = ''
        for symb in price:
            if symb >= '0' and symb <= '9':
                final_price = final_price + symb
        parsed["Price"] = final_price
    else:
        parsed["Price"] = '0'

    # comments
    comentb = items.find('div', {"class": "comments"})
    coments = comentb.find_all('li', {"class": "comments__item feedback"})
    rev_list = []
    for com in coments:
        otz = {}
        otz["Name"] = com.find('a', {"class": "feedback__header"}).text.replace(u'\n', u'')
        stars = com.find('span', {"itemprop": "reviewRating"})['class']
        otz["Mark"] = stars[2][4:]
        otz["Com"] = com.find('p', {"class": "feedback__text"}).text
        rev_list.append(otz)
    return parsed, rev_list
