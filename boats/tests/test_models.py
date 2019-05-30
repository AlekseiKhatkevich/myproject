from django.test import TestCase
from boats.models import ExtraUser, BoatImage, BoatModel
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
from articles.models import UpperHeading
import os
import datetime
from boats.utilities import set_last_access_time
from easy_thumbnails.files import get_thumbnailer
from myproject.settings import THUMBNAIL_ALIASES, MEDIA_ROOT
from django.db import models
from django.core.files.images import ImageFile

#  https://developer.mozilla.org/ru/docs/Learn/Server-side/Django/Testing
#  https://nitratine.net/blog/post/change-file-modification-time-in-python/


class ExtraUserModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        ExtraUser.objects.create(username="Testuser", first_name="Ivan", last_name="Ivanov",
                                 email="alekseikhatkevich@gmail.com", password="1q2w3e",
                                 is_active=True, is_activated=True)

    def test_first_name_label(self):
        self.user = ExtraUser.objects.get(username="Testuser")
        field_label = self.user._meta.get_field("first_name").verbose_name
        self.assertEqual(field_label, "first name")

    def test_first_name_max_length(self):
        self.user = ExtraUser.objects.get(username="Testuser")
        max_length = self.user._meta.get_field('first_name').max_length
        self.assertEquals(max_length, 30)


class BoatImageTest(TestCase):

    def setUp(self):
        #  создаем мок фото для сохранения
        image = Image.new('RGBA', size=(50, 50), color=(155, 0, 0))
        file = BytesIO(image.tobytes())
        file.name = 'test.png'
        file.seek(0)
        #  оборачиваем его в джанговский враппер для файловых объектов
        django_friendly_file = ContentFile(file.read(), 'test.png')
        # вариант основанный на уже существующем файле
        test_image = ImageFile(open(os.path.join(MEDIA_ROOT, "test_images", "test.jpg"), "rb"))

        self.upperheading = UpperHeading.objects.create(name="Articles on boats")

        self.boat_object = BoatModel.objects.create(boat_name="boat", boat_length=30,
                                                    boat_mast_type="YA", boat_keel_type="modified",
                                                    boat_price=10000, boat_country_of_origin="AX",
                                                    boat_sailboatdata_link=
                                            "https://sailboatdata.com/sailboat/bavaria-cruiser-30",
                                                    boat_description="xxx", first_year=1959,
                                                    last_year=1960, )

        self.model = BoatImage.objects.create(boat_photo=django_friendly_file, )
        self.model2 = BoatImage.objects.create(boat_photo=test_image, )

    def test_delete_old_images(self):
        """Тестируем удаление старых фоток без привязки к лодке"""
        self.model.memory = 1
        self.model.true_save()  # косяк -при сохранении мы имея только мемори записываем пк из него
        self.assertIsNone(self.model.boat)
        self.assertTrue(self.model.pk)
        self.assertTrue(self.model.memory)
        useless_old_images = BoatImage.objects.filter(boat_id__isnull=True, memory__isnull=False)
        self.assertTrue(useless_old_images.exists())
        for image in useless_old_images:
            set_last_access_time(path=image.boat_photo.path)
            self.assertTrue(datetime.datetime.now().timestamp() -
                            os.path.getmtime(image.boat_photo.path) > 5184000)
            print("Время последнего изменения ", os.path.getatime(image.boat_photo.path))
            print("Текущее время", datetime.datetime.now().timestamp())
            path = image.boat_photo.path
            self.model2.save()
            path2 = self.model2.boat_photo.path
            self.model.true_delete(), self.model2.true_delete()
            os.remove(path), os.remove(path2)
            self.tearDown()

    def test_memory_assign(self):
        """Тестируем блок памяти в коде метода save()"""
        #  первая часть
        self.model.boat = self.boat_object
        self.model.save()
        self.assertTrue(self.model.boat_id, self.model.memory)
        self.assertEqual(self.model.boat_id, self.model.memory)
        #  вторая  часть
        self.model.boat_id = None
        self.model.true_save()
        self.assertIsNone(self.model.boat_id)
        self.model.save()
        self.assertTrue(self.model.boat_id, self.model.memory)
        self.assertEqual(self.model.boat_id, self.model.memory)
        #  третья  часть
        self.model.memory = 999
        self.model.true_save()
        self.assertTrue(self.model.boat_id, self.model.memory)
        self.assertNotEqual(self.model.boat_id, self.model.memory)
        self.model.save()
        self.assertTrue(self.model.boat_id, self.model.memory)
        self.assertEqual(self.model.boat_id, self.model.memory)
        self.model.true_delete(self), self.model2.true_delete(self)
        os.remove(self.model.boat_photo.path), os.remove(self.model2.boat_photo.path)
        self.tearDown()

    def test_true_save(self):
        """Тестируем метод true_save()"""
        self.model.memory = 5
        self.model.true_save()
        self.assertEqual(self.model.memory, 5)
        self.assertIsNone(self.model.boat_id)
        os.remove(self.model.boat_photo.path), os.remove(self.model2.boat_photo.path)
        self.tearDown()

    def test_delete_thumbnails(self):
        """Тестируем удаление ассоциированных тумбнейлов в методе delete()"""
        thumbnailer = get_thumbnailer(self.model2.boat_photo)
        thumbnailer.get_thumbnail(THUMBNAIL_ALIASES[""]["default"])
        result = thumbnailer.delete_thumbnails()
        self.assertIsNotNone(result)
        self.assertNotEqual(result, 0)
        self.assertTrue(result)
        os.remove(self.model.boat_photo.path), os.remove(self.model2.boat_photo.path)
        self.tearDown()

    def test_set_fk_to_null(self):
        """Тестируем сброс фк в нулл в методе delete()"""
        self.model.boat = self.boat_object
        self.model.save()
        self.assertIsNotNone(self.model.boat_id)
        self.model.delete()
        self.assertIsNone(self.model.boat_id)
        os.remove(self.model.boat_photo.path), os.remove(self.model2.boat_photo.path)
        self.tearDown()
