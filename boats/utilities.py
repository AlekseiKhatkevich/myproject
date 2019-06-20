from django.template.loader import render_to_string
from django.core.signing import Signer
from datetime import datetime
from os.path import splitext
import os
from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import re
from currency_converter import CurrencyConverter, RateNotFoundError
import folium
from folium.plugins import MarkerCluster
import geocoder
import time
import random
from django.conf import settings
from functools import lru_cache
from django.core.cache import cache
from django.core.files import File

signer = Signer()


def files_list():
    """ список графических файлов в media"""
    spisok = set()
    allowed_extensions = ("jpg", "png", "gif", "tiff", "bmp", "psd")
    for (dirpath, dirnames, filenames) in os.walk(settings.MEDIA_ROOT):
        for file in filenames:
            if dirpath == settings.MEDIA_ROOT and file.split(".")[-1] in allowed_extensions:
                spisok.add(file)
    return spisok


def send_activation_notofication(user):
    """ функция отправки писем"""
    if settings.ALLOWED_HOSTS:
        host = "http://" + settings.ALLOWED_HOSTS[0] + ":8000"
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
                if datetime.now().timestamp() - os.path.getctime(os.path.join(dirpath,
                                                                              filename))\
                        > time_interval:  # проверяем насколько файлы старые
                    os.remove(os.path.join(dirpath, filename))


def clean_map(pk):
    """Удаляет карту при удалении лодки"""
    root = os.path.join(settings.BASE_DIR, "templates", "maps")
    file = str(pk) + ".html"
    full_path = os.path.join(root, file)
    for (dirpath, dirnames, filenames) in os.walk(root):
        if file in filenames and os.path.isfile(full_path):
            os.remove(full_path)


def currency_converter(price, curr1="SEK", curr2="EUR"):
    """конвертер валют . Работает медленно. Возвращает обменный курс"""
    c = CurrencyConverter()
    try:
        converted_price = c.convert(price, curr1, curr2)
        rate = price/converted_price
        return rate
    except ValueError or RateNotFoundError as err:
        return str(err)


def currency_converter_original(price, curr1, curr2="EUR"):
    """конвертер валют . Работает медленно.Возвращает конвертированное значение"""
    c = CurrencyConverter()
    try:
        converted_price = c.convert(price, curr1, curr2)
        return converted_price
    except ValueError or RateNotFoundError as err:
        return 0


def spider(name):
    """Поиск лодок по названию на Блоксете. Метод возвращает словарь с {названием лодки из объявления: УРЛом объявления} + список цен + словарь имя лодки: город продажи"""
    address = "https://www.blocket.se/hela_sverige?q=%s&cg=1060&w=3&st=s&ps=&pe=&c=1062&ca=11&is=1&l=0&md=li" % name.replace(" ", "+")
    try:
        html = urlopen(address)
    except HTTPError:
        return {"HTTPError": "www.blocket.se hasn't accepted the search or has other sort of"
                             " HTTP troubles "}, None, None
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
            cities_dict.update({boat: text})  # имя лодки: город
        # сортировка цен по возрастанию
        if pricelist and url_dict:
            result_list, result_dict, = zip(*sorted(zip(pricelist, url_dict.items())))
            result_list, result_dict = list(result_list), dict(result_dict)
        else:
            result_list = result_dict = {}
        # Заменяем 0 на None для корректной работы шаблона
        if 0 in result_list:
            for cnt, price in enumerate(result_list):
                if price == 0:
                    result_list[cnt] = None
        return result_dict, result_list, cities_dict


@lru_cache(maxsize=100)
def coords(city_name):
    """выдает координаты по имени города или названию места"""
    return geocoder.osm(city_name + ', Sweden').latlng


def map_folium(places: dict, pk: int):
    """Создает карту с маркерами позиций по координатам"""
    #  если у нас есть html с резульатом работы функции с теми же входными аргументами, то мы
    #  пропускаем функцию и используем готовый html файл
    if not cache.get("map_folium", version=pk) or cache.get("map_folium", version=pk) \
            != (places, pk) or not os.path.exists(os.path.join(settings.BASE_DIR, "templates",
                                                               "maps",  str(pk) +".html")):
        map = folium.Map(location=[59.20, 18.04], zoom_start=7)
        marker_cluster = MarkerCluster().add_to(map)
        known_coordinates = {}  # место: координаты
        for boat_name, place in places.items():
            # если место повторяется более 1го раза
            if list(known_coordinates.keys()).count(place) == 1:
                location = known_coordinates.get(place)
                if location:
                    # вносим корректировки в коорд. для лучшей визуализации на карте ( чтобы не
                    # кучковались метки)
                    location = [c + random.uniform(- 0.05, 0.05) for c in location]
            else:
                #  если координаты данного места еще не установленны то мы их получаем и записываем
                #  в словарь. Если это место уже известно то мы используем сохраненные координаты.
                if place not in known_coordinates.keys():
                    langalt = coords(place)  # Широта, долгота определяем
                    known_coordinates.update({place: langalt})
                location = known_coordinates.get(place)
            try:
                folium.Marker(location=location, radius=1, popup=" %s, location - %s " %
                (boat_name, place), icon=folium.Icon(color='gray')).add_to(marker_cluster)
            except TypeError:
                pass
        map.save(os.path.join(settings.BASE_DIR, "templates", "maps",  str(pk) + ".html"))
        #  Записываем в кеш входные аргументы функции (типа аналог lru_cache :))
        cache.set("map_folium", (places, pk), 60 * 60 * 24 * 7, version=pk)
    else:
        pass  # ничего не делаем так как шаблон с актуальными  данными уже есть в папке темплейтс


def set_last_access_time(path):
    """Метод изменяет время последнего изменения и время последнего доступа к файлу
    https://nitratine.net/blog/post/change-file-modification-time-in-python/"""
    fileLocation = r"%s" % path
    year = 2017
    month = 11
    day = 5
    hour = 19
    minute = 50
    second = 0
    date = datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second)
    modTime = time.mktime(date.timetuple())
    os.utime(fileLocation, (modTime, modTime))


#  https://stackoverflow.com/questions/592746/how-can-you-print-a-variable-name-in-python
def namestr(obj, namespace):
    """Возврашает строковое имя переменной
    a=2+2
    b=3+3
    ({namestr(x, globals()): x for x in (a, b)})
    {'a': 4, 'b': 6}"""
    return next(name for name in namespace if namespace[name] is obj)

