import requests
import time
import json
import re

from bs4 import BeautifulSoup
from loguru import logger

import config
from selendownloader import download


class SelConnException(Exception):
    pass


def del_spaces(text):
    while text[0] == ' ':
        text = text[1:]
    text = text[::-1]
    while text[0] == ' ':
        text = text[1:]
    return text[::-1]


def parse_ozon(URL):
    parsed = {}
    parsed['url'] = URL
    art = ''
    for symb in reversed(URL[:-1]):
        if symb >= '0' and symb <= '9':
            art = art + symb
        else:
            break
    parsed['Art'] = art[::-1]
    response = download(URL + 'reviews/')
    soup = BeautifulSoup(response, "html.parser")
    items = soup.find('div', {"class": "container e0x"})
    item = items.find('a', {"class": "ao6"})
    name = item.text
    name = name.replace(u'\n', u'')
    parsed['Name'] = del_spaces(name)
    item = items.find('span', {"class": "c2h5 c2h6"})
    price = ''
    for symb in item.find('span').text:
        if symb >= '0' and symb <= '9':
            price = price + symb
    parsed['Price'] = price
    item = soup.find('div', {"class": "_1DjF"})
    k_otz1 = item.find('span', {"class": "hRqg _13gh"}).text
    k_otz = ''
    for symb in k_otz1:
        if symb >= '0' and symb <= '9':
            k_otz = k_otz + symb
    parsed['Col_otz'] = k_otz
    # rev = ozon_rev(URL + 'reviews/')
    rev = []
    return parsed, rev


def ozon_rev(link):
    response = download(link)
    soup = BeautifulSoup(response, "html.parser")
    items = soup.find_all('div', {"class": "gb4"})
    rev_list = []
    for i in items:
        otz = {}
        name = i.find('span', {"class": "e2w5"}).text
        otz["Name"] = name
        r = i.find_all('span', {"class": "e2u6"})
        coment = ''
        stars = i.find('div', {"class": "_3xol"})['style'][6:9]
        if stars == '100':
            otz["Mark"] = 5
        elif stars == '80%':
            otz["Mark"] = 4
        elif stars == '60%':
            otz["Mark"] = 3
        elif stars == '40%':
            otz["Mark"] = 2
        else:
            otz["Mark"] = 1
        for j in r:
            coment += j.text
        otz["Com"] = coment.replace(u'\xa0', u' ')
        rev_list.append(otz)

    return rev_list


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
    response = requests.get(URL, headers=config.headers)
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


def switch(link, flag):
    s = link[12:]
    if s[0] == 'w':
        return parse_wb(link)
    else:
        try:
            return parse_ozon(link)
        except Exception as e:
            logger.warning("Сасао")
            flag += 1
            if flag <= 3:
                switch(link, flag)
            else:
                logger.exception(e)
                raise SelConnException


def main():
    while True:
        try:
            logger.info('api url:' + config.url)
            answer = requests.get(config.url + 'links/parse/',
                                  data=json.dumps({}), verify=False).json()
            logger.info('we get links')
            for i in answer:
                try:
                    logger.info(str(i['url']))
                    a = parse_wb(i['url'])
                    answer = requests.put(config.url + 'links/update/',
                                          data=json.dumps(a), verify=False)
                    logger.info('- link updated')
                except Exception as e:
                    logger.exception('error in update link:')
        except Exception as e:
            logger.error('cant connect to server, try to change API_URL in env')
            time.sleep(3)
        time.sleep(config.delay)


if __name__ == "__main__":
    main()
    # print(parse_wb("https://www.wildberries.ru/catalog/6034394/detail.aspx?targetUrl=XS"))
