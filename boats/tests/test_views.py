from django.test import TestCase
from django.shortcuts import reverse
from boats.models import BoatModel, ExtraUser


class viewname_edit_Test(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = ExtraUser.objects.create(username="Testuser", first_name="Ivan", last_name="Ivanov",
                                 email="alekseikhatkevich@gmail.com", password="1q2w3e",
                                 is_active=True, is_activated=True)


        BoatModel.objects.bulk_create([BoatModel(boat_name="boat", boat_length=30,
                                                 boat_mast_type="YA", boat_keel_type="modified",
                                                 boat_price=10000, boat_country_of_origin="AX",
                                      boat_sailboatdata_link="https://sailboatdata.com/sailboat"
                                                                        "/freedom-35-pedrick",
                                                 boat_description="xxx", first_year=1959,
                                                 last_year=1960, author=user), ])

    @classmethod
    def tearDownClass(cls):
        BoatModel.objects.all().delete()
        ExtraUser.objects.all().delete()

    def tearDown(self):
        pass

    def test_redirect_if_not_logged_in(self):
        """Проверяем , что нне прошетшего аутентификацию пользователя перенаправляет на логин
         пэйдж"""
        resp = self.client.get(reverse("boats:boat_edit", args=(1, )))
        self.assertRedirects(resp, reverse("boats:login") + "?next=" + (reverse("boats:boat_edit",
                                                                                args=(1, ))))

    def test_view_url_accessible_by_name(self):
        self.client.login(username='Testuser', password='1q2w3e')

        pk = BoatModel.objects.first().pk
        print(pk)
        resp = self.client.get(reverse("boats:boat_edit", args=(pk, )))

        self.assertEqual(resp.status_code, 200)



