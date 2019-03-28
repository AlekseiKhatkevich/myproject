from django.db import models
from django.core import validators
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser


class BoatImage(models.Model):
    boat_photo = models.ImageField(upload_to="photos/", blank=True, verbose_name='Boat photo', help_text="Please attach any photo of the boat")

    boat = models.ForeignKey("BoatModel",  on_delete=models.CASCADE, verbose_name="Boat ForeignKey", null =True)

    class Meta:
        verbose_name = "Boat photo"
        verbose_name_plural = "Boat photos"


class BoatModel(models.Model):

    SLOOP = "SL"
    KETCH = "KE"
    YAWL = "YA"
    CAT_KETCH = "CK"

    CHOICES = (
        (SLOOP, "Sloop"),
        (KETCH, "Ketch"),
        (YAWL, "Yawl"),
        (CAT_KETCH, "Cat Ketch"),
    )

    boat_name = models.CharField(max_length=50, unique=True, db_index=True, verbose_name="Boat model", help_text="Please input boat model")

    boat_length = models.FloatField(null=False, blank=False, verbose_name="Boat water-line length", help_text="Please input boat water-line length", )

    boat_description = models.TextField(blank=True, verbose_name="Boat description", help_text="Please describe the boat")

    boat_mast_type = models.CharField(max_length=10, choices=CHOICES, default=SLOOP, verbose_name="Boat rigging type", help_text="Please input boat rigging type")

    boat_price = models.PositiveSmallIntegerField(verbose_name="price of the boat", help_text="Please input boat price", )

    boat_country_of_origin = models.CharField(max_length=20, verbose_name="Boat country of origin", help_text="Please specify boat's country of origin")

    boat_sailboatdata_link = models.URLField(max_length=100, blank=True, verbose_name="URL to Sailboatdata", help_text="Please type in URL to Sailboatdata page for this boat")

    boat_keel_type = models.CharField(max_length=50, verbose_name="Boat keel type", help_text="Please specify boat's keel type")

    boat_publish_date = models.DateTimeField(auto_now_add=True)

    boat_primary_photo = models.ImageField(upload_to="photos/", blank=False, verbose_name='Boat primary photo', help_text="Please attach a primary photo of the boat")

    def __str__(self):
        return self.boat_name

    class Meta:
        verbose_name = "Boats primary data"
        verbose_name_plural = "Boats primary data"
        ordering = ["boat_name"]

    def length_mast_keel(self):
        if self.boat_length and self.boat_keel_type and self.boat_mast_type:
            return "length - %d feet, keel type - %s, rigging - %s" % (self.boat_length, self.boat_keel_type,  self.boat_mast_type)

    def clean(self):
        errors = {}
        if self.boat_length and self.boat_length < 10:
            errors["boat_length"] = ValidationError("waterline length seems to short")
        if self.boat_price and self.boat_price < 5000:
            errors["boat_price"] = ValidationError("PRICE:Are you sure? It's almost free! ")
        if errors:
            raise ValidationError(errors)


class ExtraUser(AbstractUser):
    is_activated = models.BooleanField(default=True, db_index=True, verbose_name="Is user activated?", help_text= "Specifies whether user has been activated or not")

    class Meta(AbstractUser.Meta):
        pass




