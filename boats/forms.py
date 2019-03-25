from django.forms import ModelForm
from .models import *


class BoatForm(ModelForm):
    class Meta:
        model = BoatModel
        fields = ("boat_name", "boat_length", "boat_mast_type", "boat_keel_type", "boat_primary_photo", "boat_description", "boat_price", "boat_country_of_origin", "boat_sailboatdata_link ", "boat_primary_photo" )
