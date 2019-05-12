from django.template.loader import render_to_string
from django.core.signing import Signer
from myproject.settings import ALLOWED_HOSTS, MEDIA_ROOT
from datetime import datetime
from os.path import splitext
import os


signer = Signer()


def files_list():
    """ список файлов в media"""
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
    return "%s%s" % (datetime.now().timestamp(), splitext(filename)[1])


def clean_cache(path, time_interval):  # https://pastebin.com/0SPBLJfD
    """Очистка кэша ресубмита """
    if os.path.exists(path) and os.path.isdir(path):
        for (dirpath, dirnames, filenames) in os.walk(path):
            for filename in filenames:
                if datetime.now().timestamp() - os.path.getctime(os.path.join(dirpath, filename)) > \
                        time_interval:  # проверяем насколько файлы старые
                    os.remove(os.path.join(dirpath, filename))




