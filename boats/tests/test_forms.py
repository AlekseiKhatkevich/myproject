from django.test import TestCase, SimpleTestCase
from boats.forms import BoatForm
import requests
from boats.utilities import currency_converter_original


form_data = {"boat_name": "boat",
                 "boat_length": 30,
                 "boat_mast_type": "YA",
                 "boat_keel_type": "modified",
                 "boat_price": 4000,
                 "boat_country_of_origin": "AX",
                 "boat_sailboatdata_link": "https://sailboatdata.com/sailboat/bavaria-cruiser-30",
                 "boat_description": "xxx",
                 "first_year": 1961,
             "last_year": 1962,
             "currency": "SEK"},



form = BoatForm(data=form_data)


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
        data = self.form_data
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

