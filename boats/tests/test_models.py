from django.test import TestCase
from boats.models import ExtraUser, BoatImage, BoatModel
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile
from articles.models import UpperHeading, Article, SubHeading
import os
import datetime
from boats.utilities import set_last_access_time
from easy_thumbnails.files import get_thumbnailer
#from myproject.settings import THUMBNAIL_ALIASES, MEDIA_ROOT, BASE_DIR, CACHES
from django.conf import settings
from django.db import models


#  https://developer.mozilla.org/ru/docs/Learn/Server-side/Django/Testing
#  https://nitratine.net/blog/post/change-file-modification-time-in-python/


class ExtraUserModelTest(TestCase):
    """Тестируем расширенную модель пользователя"""

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

    @classmethod
    def tearDownClass(cls):
        ExtraUser.objects.all().delete()


class BoatImageTest(TestCase):
    """Тестируем модель изображений"""

    @classmethod
    def setUpTestData(cls):
        UpperHeading.objects.create(name="Articles on boats")

    def setUp(self):
        #  создаем мок фото для сохранения
        image = Image.new('RGBA', size=(50, 50), color=(155, 0, 0))
        file = BytesIO(image.tobytes())
        file.name = 'test.png'
        file.seek(0)
        #  оборачиваем его в джанговский враппер для файловых объектов
        django_friendly_file = ContentFile(file.read(), 'test.png')
        # вариант основанный на уже существующем файле
        test_image = ImageFile(open(os.path.join(settings.MEDIA_ROOT, "test_images", "test.jpg"),
                                    "rb"))

        self.boat_object = BoatModel.objects.create(boat_name="boat", boat_length=30,
                                                    boat_mast_type="YA", boat_keel_type="modified",
                                                    boat_price=10000, boat_country_of_origin="AX",
                                                    boat_sailboatdata_link=
                                            "https://sailboatdata.com/sailboat/bavaria-cruiser-30",
                                                    boat_description="xxx", first_year=1959,
                                                    last_year=1960, )

        self.model = BoatImage.objects.create(boat_photo=django_friendly_file, )
        self.model2 = BoatImage.objects.create(boat_photo=test_image, )

    def tearDown(self):
        try:
            self.model.refresh_from_db()
            self.model.true_delete()
        except self.model.DoesNotExist:
            pass
        self.model2.true_delete()
        os.remove(self.model.boat_photo.path), os.remove(self.model2.boat_photo.path)
        self.boat_object.delete()

    @classmethod
    def tearDownClass(cls):
        UpperHeading.objects.get(name="Articles on boats").delete()
        BoatModel.objects.all().delete()
        BoatImage.objects.all().delete()

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
            #  print("Время последнего изменения ", os.path.getatime(image.boat_photo.path))
            #  print("Текущее время", datetime.datetime.now().timestamp())
            self.model2.save()
            self.assertFalse(BoatImage.objects.filter(pk=self.model.pk).exists())

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

    def test_true_save(self):
        """Тестируем метод true_save()"""
        self.model.memory = 5
        self.model.true_save()
        self.assertEqual(self.model.memory, 5)
        self.assertIsNone(self.model.boat_id)

    def test_delete_thumbnails(self):
        """Тестируем удаление ассоциированных тумбнейлов в методе delete()"""
        thumbnailer = get_thumbnailer(self.model2.boat_photo)
        thumbnailer.get_thumbnail(settings.THUMBNAIL_ALIASES[""]["default"])
        result = thumbnailer.delete_thumbnails()
        self.assertIsNotNone(result)
        self.assertNotEqual(result, 0)
        self.assertTrue(result)

    def test_set_fk_to_null(self):
        """Тестируем сброс фк в нулл в методе delete()"""
        self.model.boat = self.boat_object
        self.model.save()
        self.assertIsNotNone(self.model.boat_id)
        self.model.delete()
        self.model.refresh_from_db()
        self.assertIsNone(self.model.boat_id)

    def test_set_utime(self):
        """Тестируем установку времени изменения файла на сейчас при его удалении"""
        self.boat_object.boatimage_set.add(self.model)
        self.model.delete()
        #  print("Время последнего изменения ", os.path.getatime(self.model.boat_photo.path))
        #  print("Текущее время", datetime.datetime.now().timestamp())
        self.assertAlmostEqual(datetime.datetime.now().timestamp(),
                               os.path.getmtime(self.model.boat_photo.path))

    def test_true_delete(self):
        """тестируем метод true_delete()"""
        self.model.true_delete()
        self.assertFalse(BoatImage.objects.filter(pk=self.model.pk).exists())


class BoatModelTest(TestCase):
    """Тестируем модель лодки"""

    @classmethod
    def setUpTestData(cls):
        UpperHeading.objects.create(name="Articles on boats")
        ExtraUser.objects.create(username="Testuser2", first_name="Ivan", last_name="Petrov",
                                 email="email@gmail.com", password="1q2w3e",
                                 is_active=True, is_activated=True)

        image = Image.new('RGBA', size=(50, 50), color=(155, 0, 0))
        file = BytesIO(image.tobytes())
        file.name = 'test.png'
        file.seek(0)
        #  оборачиваем его в джанговский враппер для файловых объектов
        django_friendly_file = ContentFile(file.read(), 'test.png')
        # вариант основанный на уже существующем файле
        test_image = ImageFile(open(os.path.join(settings.MEDIA_ROOT, "test_images", "test.jpg"),
                                    "rb"))

        BoatImage.objects.create(boat_photo=django_friendly_file, )
        BoatImage.objects.create(boat_photo=test_image, )

    @classmethod
    def tearDownClass(cls):
        for image in BoatImage.objects.all():
            os.remove(image.boat_photo.path)
            image.true_delete()
        UpperHeading.objects.all().delete()
        ExtraUser.objects.all().delete()
        SubHeading.objects.all().delete()
        BoatModel.objects.all().delete()

    def setUp(self):
        self.boat_object = BoatModel.objects.create(boat_name="boat", boat_length=30,
                                                    boat_mast_type="YA", boat_keel_type="modified",
                                                    boat_price=10000, boat_country_of_origin="AX",
                                boat_sailboatdata_link="https://sailboatdata.com/sailboat/bavaria"
                                                       "-cruiser-30",
                                                    boat_description="xxx", first_year=1959,
                                                    last_year=1960, )

        self.subheading = SubHeading.objects.create(foreignkey_id=UpperHeading.objects.get(
            name="Articles on boats").pk, name="subheading")

        self.article = Article.objects.create(foreignkey_to_subheading=self.subheading,
                                              title="Article", content="X",
                                              author=ExtraUser.objects.first(),
                            url_to_article="https://pythonworld.ru/moduli/modul-unittest.html",)

    def tearDown(self):
        pass

    def test_delete_empty_subheadings(self):
        """Тестируем удаление пустых подзаголовков в методе delete()"""
        # 1 находится в папке Articles on boats
        # 2 нет связи с лодкой
        # 3 нет связанных статей
        self.article.true_delete()
        self.assertEqual(self.subheading.foreignkey_id, self.subheading.foreignkey.pk)
        self.assertIsNone(self.subheading.one_to_one_to_boat)
        self.assertFalse(self.subheading.article_set.exists())
        self.boat_object.delete()
        self.assertFalse(SubHeading.objects.filter(pk=self.subheading.pk).exists())

    def test_protect_subheadings_from_deletion(self):
        """тестируем случай, в котором подзаголовок содержит статьи. Он не должен быть удален в
        таком случае"""
        self.boat_object.delete()
        self.assertTrue(SubHeading.objects.filter(pk=self.subheading.pk).exists())

    def test_delete_connected_subheadings(self):
        """Тестируем систему удаления подзаголовков связанных с лодкой при удалении самой лодки, в
         случае если подзаголовок не содержит статей"""
        #  привязываем текущую лодку к подзаголовку
        self.subheading.one_to_one_to_boat = self.boat_object
        self.assertTrue(SubHeading.objects.filter(one_to_one_to_boat=self.boat_object).exists())
        self.article.true_delete()
        self.assertFalse(SubHeading.objects.get(
                    one_to_one_to_boat=self.boat_object).article_set.exists())
        self.boat_object.delete()
        self.assertFalse(SubHeading.objects.filter(pk=self.subheading.pk).exists())

    def test_protect_connected_subheading_from_deletion(self):
        """Тестируем случай, когда связанная с лодкой подкатегоря содержит вложенную статью и
         подкатегория и статья не должны в таком случае удаляться"""
        self.subheading.one_to_one_to_boat_id = self.boat_object.pk
        self.assertEqual(self.subheading.one_to_one_to_boat_id, self.boat_object.pk)
        self.assertTrue(SubHeading.objects.filter(one_to_one_to_boat=self.boat_object).exists())
        self.assertEqual(self.subheading.pk, self.article.foreignkey_to_subheading_id)
        self.boat_object.delete()
        self.assertTrue(SubHeading.objects.filter(pk=self.subheading.pk).exists())
        self.assertTrue(Article.objects.filter(pk=self.article.pk).exists())

    def test_images_deletion(self):
        """ Проверяем хук метода delete() BoatImage при срабатывании метода delete() BoatModel"""
        image2 = BoatImage.objects.get(pk=2)
        #  создаем тумбнейлы
        thumbnailer = get_thumbnailer(image2.boat_photo)
        thumbnailer.get_thumbnail(settings.THUMBNAIL_ALIASES[""]["default"])

        self.boat_object.boatimage_set.add(image2)
        self.assertEqual(self.boat_object.id, image2.boat_id)
        self.boat_object.delete()
        image2.refresh_from_db()
        self.assertIsNone(image2.boat_id)
        self.assertAlmostEqual(datetime.datetime.now().timestamp(),
                               os.path.getmtime(image2.boat_photo.path), places=1)
        #  Пробуем удалить тумбнейлы. Метод возвращает кол-во удаленных тумбнейлов. Если их ноль
        #  -то они уже были удалены и все чики-пуки
        result = thumbnailer.delete_thumbnails()
        self.assertEqual(result, 0)

    def test_map_cleanup(self):
        """Проверка удаления карты после удаления лодки. Метод delete()"""
        #  создаем файл карты
        filename = str(self.boat_object.pk)
        path = os.path.join(settings.BASE_DIR, 'templates', "maps",  filename + '.html')
        f = open(path, "wb")
        f.seek(10737 - 1)
        f.write(b"\0")
        f.close()
        self.assertTrue(os.path.exists(path))
        self.boat_object.delete()
        #  файл карты должен быть удален
        self.assertFalse(os.path.exists(path))

    def test_save_clean_cache(self):
        """Проверка удаления кэша ресубмита """
        path = settings.CACHES.get("file_resubmit").get("LOCATION")
        #  кол-во файлов со сроком создания более 1 дня
        old_files_count = 0
        for (dirpath, dirnames, filenames) in os.walk(path):
            for filename in filenames:
                old_files_count += 1 if datetime.datetime.now().timestamp() - os.path.getctime(
                    os.path.join(dirpath, filename)) > 86400 else 0
        #  общее кол-во файлов в папке
        num_files = sum(os.path.isfile(os.path.join(path, f)) for f in os.listdir(path))
        self.boat_object.save()
        #  Если нет старых файлов то общее кол-во файлов в папке до и после save() должно быть
        #  одинаковым, т.е файлы не были удалены
        if old_files_count == 0:
            self.assertEqual(num_files, sum(os.path.isfile(os.path.join(path, f))
                                                  for f in os.listdir(path)))
        else:  # если есть старые файлы то они будут удалены и кол-во файлов до и после должно
            # разниться
            self.assertNotEqual(num_files, sum(os.path.isfile(os.path.join(path, f))
                                                  for f in os.listdir(path)))

