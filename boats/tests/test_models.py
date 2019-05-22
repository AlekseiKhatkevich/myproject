from django.test import TestCase, SimpleTestCase
import unittest
from boats.models import ExtraUser
#  https://developer.mozilla.org/ru/docs/Learn/Server-side/Django/Testing


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
