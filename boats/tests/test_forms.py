from django.test import TestCase
from boats.forms import BoatForm, NewUserForm, ExtraUser, PRForm, PwdChgForm, AuthCustomForm
import requests
from boats.utilities import currency_converter_original
from django import forms
from unittest.mock import MagicMock
from boats.models import user_registrated, BoatModel
from django.core.exceptions import NON_FIELD_ERRORS
from articles.models import SubHeading, Heading
from django.core.exceptions import ValidationError
from django.test.utils import override_settings
from django.conf import settings


class BoatFormTest(TestCase):
    """Тестируем форму новой лодки"""
    form_data = {"boat_name": "boat",
                 "boat_length": 30,
                 "boat_mast_type": "YA",
                 "boat_keel_type": "modified",
                 "boat_price": 10000,
                 "boat_country_of_origin": "AX",
                 "boat_sailboatdata_link":
                 "https://sailboatdata.com/sailboat/bavaria-cruiser-30",
                 "boat_description": "xxx",
                 "first_year": 1959,
                 "last_year": 1960,
                 "currency": "EUR"}

    def tearDown(self):
        SubHeading.objects.all().delete()
        Heading.objects.all().delete()
        BoatModel.objects.all().delete()

    @classmethod
    def tearDownClass(cls):
        del cls.form_data
        BoatModel.objects.all().delete()

    def test_manufacturing_years_false(self):
        """Проверяем, что если ввести год начала пр-ва старше года окончания пр-ва то валидация
        не проходит"""
        data = self.form_data.copy()
        data["first_year"], data["last_year"] = 1960, 1959
        form = BoatForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors.get("last_year") == ['Last year has to be superior then'
                                                         ' first year'])
        form.errors.clear()

    def test_manufacturing_years_true(self):
        """Проверка валидации корректно заполненной формы"""
        data = self.form_data.copy()
        form = BoatForm(data=data)
        self.assertTrue(form.is_valid())

    def test_url_sailboatdata(self):
        """Проверка возникновения ошибки при неправильном урле"""
        msg3 = "This URL does not work!"
        msg4 = "Please provide url exactly to 'sailboatdata.com' "
        msg5 = "Connection error"
        data = self.form_data.copy()
        #  проверка при неправильном урле
        data["boat_sailboatdata_link"] = "https://sailboatdata.com/sailboat/bavaria-cruiser-xxx"
        form = BoatForm(data=data)
        request = requests.head(data.get("boat_sailboatdata_link"))
        self.assertFalse(form.is_valid())
        self.assertFalse(request.status_code // 100 == 2)
        self.assertTrue(form.errors.get("boat_sailboatdata_link") == [msg3])
        form.errors.clear()

        # урл правильный, но не на "sailboatdata"
        data = self.form_data.copy()
        data["boat_sailboatdata_link"] = \
            "https://docs.djangoproject.com/en/2.2/ref/forms/validation/"
        form = BoatForm(data=data)
        request = requests.head(data.get("boat_sailboatdata_link"))
        self.assertTrue(request.status_code // 100 == 2)
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors.get("boat_sailboatdata_link") == [msg4])
        form.errors.clear()

        # проверка на ошибку связи
        data = self.form_data.copy()
        data["boat_sailboatdata_link"] = "https://devefgbghbghnghng.com"
        form = BoatForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors.get("boat_sailboatdata_link") == [msg5])
        form.errors.clear()

    def test_price_level(self):
        """Проверям, чтобы цена не была менее 5000 euro. Работа валидатора формы"""
        # Для создаваемой лодки
        msg = "Are you sure? It is almost free!"
        data = self.form_data.copy()
        data["currency"] = "SEK"
        data["boat_price"] = 10000
        form = BoatForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors.get("boat_price"))
        form.errors.clear()

        # для редактируемой лодки
        data["currency"] = "EUR"
        data["boat_price"] = 4000
        form = BoatForm(data=data, pk=1)
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors.get("boat_price") == [msg])
        form.errors.clear()

    def test_years_choices(self):
        """Проверяем работу генератора годов"""
        data = self.form_data.copy()
        form = BoatForm(data=data)
        self.assertEqual(list(form.fields["first_year"].choices), list(form.fields[
                                                                            "last_year"].choices))
        #  Проверяем , чтобы choices не были пустыми
        self.assertNotEqual(list(form.fields["first_year"].choices), [])
        self.assertNotEqual(list(form.fields["last_year"].choices), [])

    def test_currency_choices(self):
        """Проверяем работу генератора валют"""
        data = self.form_data.copy
        form = BoatForm(data=data)
        self.assertNotEqual(list(form.fields["currency"].choices), [])

    def test_HiddenInput_currency(self):
        """Проверяем, чтобы в форме редактирования лодки поле "currency" было скрытым и оно не
        требовалось к занесению"""
        data = self.form_data.copy
        form = BoatForm(data=data, pk=1)
        self.assertEqual("<class 'django.forms.widgets.HiddenInput'>", str(type(form.fields[
                                                                            "currency"].widget)))
        self.assertFalse(form.fields["currency"].required)
        self.assertIsInstance(form.fields["currency"].widget, forms.HiddenInput)

    def test_UniqueNameValidator(self):
        """Тестируем кастомный валидатор UniqueNameValidator:"""
        Heading.objects.create(name="heading")
        SubHeading.objects.create(name="boat", foreignkey_id=1)
        self.assertTrue(SubHeading.objects.filter(name="boat").exists())
        data = self.form_data.copy()
        form = BoatForm(data=data)
        message = "Subheading with this name is already exists. Please choose an alternative " \
                  "name or slightly correct current one"
        self.assertFalse(form.is_valid())
        self.assertEqual([message], form.errors.get("boat_name"))

    @override_settings(DEBUG=False)
    def test_UniqueSailboatLinkValidator(self):
        """Тестируем работу кастомного валидатора UniqueSailboatLinkValidator"""
        self.assertFalse(settings.DEBUG)
        BoatModel.objects.bulk_create([BoatModel(boat_name="boat", boat_length=30,
                                 boat_mast_type="YA", boat_keel_type="modified",
                                 boat_price=10000, boat_country_of_origin="AX",
                                 boat_sailboatdata_link="https://sailboatdata.com/sailboat"
                                                        "/freedom-35-pedrick",
                                 boat_description="xxx", first_year=1959,
                                 last_year=1960, ), ])
        data = self.form_data.copy()
        data.update({
            "boat_sailboatdata_link": "https://sailboatdata.com/sailboat/freedom-35-pedrick"})
        form = BoatForm(data=data)
        self.assertTrue(BoatModel.objects.filter(
            boat_sailboatdata_link="https://sailboatdata.com/sailboat/freedom-35-pedrick"
                                   "").exists())
        self.assertEquals("https://sailboatdata.com/sailboat/freedom-35-pedrick",
                          data["boat_sailboatdata_link"])
        message = 'same link to the  "Sailboatdata" is already exist in database!'
        self.assertFalse(form.is_valid())
        self.assertEqual([message], form.errors.get("boat_sailboatdata_link"))


class NewUserFormTestCase(TestCase):
    """Тестируем форму регистрации нового пользователя"""
    form_data = {
            "email": "tatata@inbox.ru",
            "password1": "NUio7derT",
            "password2": "NUio7derT",
            "username": "Valera"
    }

    @classmethod
    def tearDownClass(cls):
        del cls.form_data

    def test_clean_password(self):
        """Проверка валидатора пароля 1"""
        data = self.form_data.copy()
        form = NewUserForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertFalse(form.errors.get('password1'))

    def test_clean_method(self):
        """Проверка метода клин"""
        data = self.form_data.copy()
        data["password2"] = "AAAAAAAAAAAA"
        form = NewUserForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.get("password2"), ["Passwords aren't coincide!"])

    def test_signal(self):
        """Тест прохождения сигнала при сохранении формы"""
        handler = MagicMock()
        user_registrated.connect(handler, sender=NewUserForm)
        data = self.form_data.copy()
        form = NewUserForm(data=data)
        user = form.save()
        handler.assert_called_once_with(signal=user_registrated, instance=user, sender=NewUserForm)


class PRFormTestCase(TestCase):
    """Тестируем форму сброса пароля (первую часть ее)"""

    form_data = {
        "email": "aaaaa@inbox.ru"
        }

    @classmethod
    def tearDownClass(cls):
        del cls.form_data

    def setUp(self):
        self.user = ExtraUser.objects.create(
            email="kkkk@inbox.ru",
            password="NUio7derT",
            username="Vasya",
            first_name="Vasya",
            last_name="Ivanov",
        )

    def test_no_user_with_such_email(self):
        """Случай когда такого емейла нет в базе"""
        form = PRForm(data=self.form_data.copy())
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.get("email"),
                         ["There is no user registered with the specified E-Mail address."])

    def test_user_is_not_active(self):
        """Случай, когда емейл есть в базе но акк. деактивированн"""
        form = PRForm(data=self.form_data.copy())
        self.user.is_active = False
        self.user.email = "aaaaa@inbox.ru"
        self.user.save()
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.get("email"),
                         ["This account had been deactivated or wasn't activated at all."])
        self.tearDown()


class PwdChgFormTestCase(TestCase):
    """Тест формы смены пароля"""

    def setUp(self):
        self.user = ExtraUser.objects.create(
            email="kkkk@inbox.ru",
            password="NUio7derT",
            username="Vasya",
            first_name="Vasya",
            last_name="Ivanov",)

    form_data = {
        'old_password': "NUio7derT",
        'new_password1': "Lakemanitoba58967",
        'new_password2': "Lakemanitoba58967",
    }

    @classmethod
    def tearDownClass(cls):
        del cls.form_data

    def test_form_behavior(self):
        """Проверяем отправку сигнала при сохранении формы"""
        handler = MagicMock()
        user_registrated.connect(handler, sender=PwdChgForm)
        form = PwdChgForm(data=self.form_data.copy(), user=self.user)
        form.is_valid()
        form.save(commit=False)
        self.assertFalse(self.user.is_activated, self.user.is_active)
        handler.assert_called_once_with(signal=user_registrated, instance=self.user,
                                        sender=PwdChgForm)


class AuthCustomFormTestCase(TestCase):
    """Проверка формы лог-ин"""

    def setUp(self):
        self.user = ExtraUser.objects.create(
            email="kkkk@inbox.ru",
            password="NUio7derT",
            username="Vasya",
            first_name="Vasya",
            last_name="Ivanov",)

        self.form_data = {"username": "Vasya", "password": "NUio7derT"}

    def tearDown(self):
        self.user.delete()
        del self.form_data

    def test_user_is_active_false(self):
        """Тестируем случай когда пользователь не активирован и пытается зайти на сайт"""
        form = AuthCustomForm(data=self.form_data)
        self.user.is_active = False
        self.user.save()
        message = "Account '%(value)s' has been deactivated or wasn't activated at all" % \
                  {"value": self.user.username}
        self.assertIn(message, form.errors.get('__all__'))

    def test_invalid_login(self):
        """Тестируем случай когда пользователь ввел неправильный логин и(или) пароль"""
        form = AuthCustomForm({"username": "XXXX", "password": "YYYY"})
        self.assertFalse(form.is_valid())



