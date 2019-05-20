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
            if final_search:
                #  достаем урл
                url = (re.findall(r"http(?:s)?://\S+", str(final_search)))
                title = final_search.get_text()
                url_dict.update({title: url[0][: -1]})
            else:
                url = (re.findall(r"http(?:s)?://\S+", str(unit)))
                title = unit.get_text()
                if not title.isspace():
                    url_dict.update({title: url[0][: -1]})

    print(url_dict)
    print(len(url_dict))
spider("Smaragd")
#[295000, 86000, 80000, 80000, 230000, 129000, 160000, 170000, 130000, 89000, 250000]
