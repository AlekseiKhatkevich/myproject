from __future__ import absolute_import, unicode_literals
from celery import shared_task
from .models import BoatImage
from .utilities import files_list
import os
from myproject.settings import MEDIA_ROOT
from datetime import datetime
from myproject.settings import CACHES
from myproject.celery import app


@app.task
def clean_media_root():
    """метод очистки лишних изображений в медиа рут"""
    files_in_db = {image.filename() for image in BoatImage.objects.all().only("boat_photo")}
    useless_files = files_list() - files_in_db
    counter = 0
    for file in useless_files:
        os.remove(os.path.join(MEDIA_ROOT, file))
        counter += 1
    print(counter, "\xa0\\files were removed from MEDIA_ROOT")


@app.task
def add(x, y):
    return x + y


@app.task
def mul(x, y):
    return x * y


@app.task
def xsum(numbers):
    return sum(numbers)


@app.task
def clean_cache(path=CACHES.get("file_resubmit").get("LOCATION"), time_interval=86400):  # https://pastebin.com/0SPBLJfD
    """Очистка кэша ресубмита """
    files_number = 0
    deleted_number = 0
    if os.path.exists(path) and os.path.isdir(path):
        for (dirpath, dirnames, filenames) in os.walk(path):
            for cnt, filename in enumerate(filenames):
                files_number = cnt
                if datetime.now().timestamp() - os.path.getctime(os.path.join(dirpath, filename)) > \
                        time_interval:  # проверяем насколько файлы старые
                    os.remove(os.path.join(dirpath, filename))
                    deleted_number += 1
    print("Files checked-->", files_number)
    print("Files deleted-->", deleted_number)
