from django.template.loader import render_to_string
from django.core.signing import Signer
from myproject.settings import ALLOWED_HOSTS, MEDIA_ROOT
from datetime import datetime
from os.path import splitext
import os
from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import re
from currency_converter import CurrencyConverter, RateNotFoundError


signer = Signer()


def files_list():
    """ список графических файлов в media"""
    spisok = set()
    allowed_extensions = ("jpg", "png", "gif", "tiff", "bmp", "psd")
    for (dirpath, dirnames, filenames) in os.walk(MEDIA_ROOT):
        for file in filenames:
            if dirpath == MEDIA_ROOT and file.split(".")[-1] in allowed_extensions:
                spisok.add(file)
    return spisok


def send_activation_notofication(user):
    """ функция отправки писем"""
    if ALLOWED_HOSTS:
        host = "http://" + ALLOWED_HOSTS[0]
    else:
        host = "http://localhost:8000"
    context = {"user": user, "host": host, "sign": signer.sign(user.username)}
    subject = render_to_string("email/activation_letter_subject.txt", context)
    body_text = render_to_string("email/activation_letter_body.txt", context)
    user.email_user(subject, body_text)


def get_timestamp_path(instance, filename):
    """функция уникального имени сохраняемого файла"""
    return "%s%s" % (datetime.now().timestamp(), splitext(filename)[1])


def clean_cache(path, time_interval):  # https://pastebin.com/0SPBLJfD
    """Очистка кэша ресубмита """
    if os.path.exists(path) and os.path.isdir(path):
        for (dirpath, dirnames, filenames) in os.walk(path):
            for filename in filenames:
                if datetime.now().timestamp() - os.path.getctime(os.path.join(dirpath, filename)) > \
                        time_interval:  # проверяем насколько файлы старые
                    os.remove(os.path.join(dirpath, filename))


def currency_converter(price, curr1="SEK", curr2="EUR"):
    """конвертер валют . Работает медленно"""
    c = CurrencyConverter()
    try:
        converted_price = c.convert(price, curr1, curr2)
        rate = price/converted_price
        return rate
    except ValueError or RateNotFoundError as err:
        return str(err)


def spider(name):
    """Поиск лодок по названию на Блоксете. Метод возвращает словарь с {названием лодки из объявления:
     УРЛом объявления} + список цен"""
    address = "https://www.blocket.se/hela_sverige?q=%s&cg=1060&w=3&st=s&ps=&pe=&c=1062&ca=11&is=1&l=0&md=li" % name.replace(" ", "+")
    try:
        html = urlopen(address)
    except HTTPError:
        return {"HTTPError": "www.blocket.se hasn't accepted the search or has other sort of HTTP "
                           "troubles "}
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
                url_dict.update({title: url[0][: -1]})  # словарь ценаЖ урл
                #  Ищем цены
        prices = bsObj.findAll("p", {"itemprop": "price"})
        pricelist = []
        for price in prices:  # why dont just use API instead ??? LOL
            #  отбираем только цену. Фильтруем таги и др. хрень
            digits = ''.join(filter(lambda x: x.isdigit(), price.get_text()))
            pricelist.append(int(digits)) if digits else pricelist.append(0)

        # ищем места продажи лодок
        places = bsObj.find_all("header", {"itemprop": "itemOffered"})
        cities = {}
        names_iterator = iter(url_dict.keys())
        for place in places:
            # отделяем экранированные символы от текста и шлак в начале строки
            letters = ''.join(filter(lambda x: False if x.isspace() else True,
                                         place.get_text()[15:]))
            cities.update({next(names_iterator): letters})  # имя лодки: город

        # сортировка цен по возрастанию
        result_list, result_dict, = zip(*sorted(zip(pricelist, url_dict.items())))
        result_list, result_dict = list(result_list), dict(result_dict)
        # Заменяем 0 на None для корректной работы шаблона
        if 0 in result_list:
            for cnt, price in enumerate(result_list):
                if price == 0:
                    result_list[cnt] = None

        return result_dict, result_list, cities

spider("najad")
