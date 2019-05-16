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


""" функция отправки писем"""


def send_activation_notofication(user):
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
            final_search = bsObj.find("a", {"tabindex": "50", "title": unit.get_text()})
            if final_search:
                url = (re.findall(r"http(?:s)?://\S+", str(final_search)))
                title = final_search.get_text()
                url_dict.update({title: url[0][: -1]})
                #  Ищем цены
        prices = bsObj.findAll("p", {"itemprop": "price"})
        pricelist = []
        for price in prices:  # why dont just use API instead ??? LOL
            digits = ''.join(filter(lambda x: x.isdigit(), price.get_text()))
            pricelist.append(int(digits)) if digits else pricelist.append(None)
        return url_dict, pricelist

