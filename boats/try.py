import os
from myproject.settings import MEDIA_ROOT





def files_list():
    """ список файлов в media"""
    spisok = set()
    allowed_extensions = ("jpg", "png", "gif", "tiff", "bmp", "psd")
    for (dirpath, dirnames, filenames) in os.walk(MEDIA_ROOT):
            for file in filenames:
                if dirpath == MEDIA_ROOT and file.split(".")[-1] in allowed_extensions:
                    spisok.add(file)
    return spisok

print(files_list())
print(len(files_list()))
