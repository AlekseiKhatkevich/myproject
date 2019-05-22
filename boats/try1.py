import os
from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import re
from currency_converter import CurrencyConverter, RateNotFoundError



def spider(name):
    """Поиск лодок по названию на Блоксете. Метод возвращает словарь с {названием лодки из объявления: УРЛом объявления} + список цен + словарь имя лодки: город продажи"""
    address = "https://www.blocket.se/hela_sverige?q=%s&cg=1060&w=3&st=s&ps=&pe=&c=1062&ca=11&is=1&l=0&md=li" % name.replace(" ", "+")
    try:
        html = urlopen(address)
    except HTTPError:
        return {"HTTPError": "www.blocket.se hasn't accepted the search or has other sort of HTTP "
                           "troubles "}, None, None
    else:
        bsObj = BeautifulSoup(html.read(), features="lxml")

        #  ищем названиия объявлений и урлы лодок
        raw_search = bsObj.findAll("a", {"tabindex": "50"})
        url_dict = {}
        for unit in raw_search:
            # ищем теги где в названииях есть имя лодки
            final_search = bsObj.find("a", {"tabindex": "50", "title": unit.get_text()})
            if final_search:  # если поиск сработал
                #  достаем урл
                url = (re.findall(r"http(?:s)?://\S+", str(final_search)))
                title = final_search.get_text()
                url_dict.update({title: url[0][: -1]})  # словарь цена: урл
            else:  # если не сработал то пробуем извлечь данные в сыром поиске
                url = (re.findall(r"http(?:s)?://\S+", str(unit)))
                title = unit.get_text()
                if not title.isspace():  # отсекаем строки с экранированными символами
                    url_dict.update({title: url[0][: -1]})
                #  Ищем цены
        prices = bsObj.findAll("p", {"itemprop": "price"})
        pricelist = []
        for price in prices:  # why dont just use API instead ??? LOL
            #  отбираем только цену. Фильтруем таги и др. хрень
            digits = ''.join(filter(lambda x: x.isdigit(), price.get_text()))
            pricelist.append(int(digits)) if digits else pricelist.append(0)
        # ищем места продажи лодок (возвращаемый словарь не сортирован по уровню цен)
        places = bsObj.find_all("header", {"itemprop": "itemOffered"})
        cities_dict = {}  # лодка : город
        for place, boat in zip(places, url_dict.keys()):
            # отделяем экранированные символы от текста и шлак в начале строки
            text = place.get_text().strip().split()[-1]
            print(boat, text)
            cities_dict.update({boat: text})  # имя лодки: город




if __name__ ==  "__main__":

    spider("Najad")
#[295000, 86000, 80000, 80000, 230000, 129000, 160000, 170000, 130000, 89000, 250000]
