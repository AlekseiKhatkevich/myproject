from django.db import models


class BoatModel(models.Model):

    SLOOP = "SL"
    KETCH = "KE"
    YAWL = "YA"
    CAT_KETCH = "CK"

    CHOICES = (
        (SLOOP, "Sloop"),
        (KETCH, "Ketch"),
        (YAWL, "YAWL"),
        (CAT_KETCH, "Cat Ketch"),
    )

    boat_name = models.CharField(max_length=50, unique=True, primary_key=True, verbose_name="Boat model", help_text="Please input boat model")
    boat_length = models.FloatField(null=False, blank=False, verbose_name="Boat water-line length", help_text="Please input boat water-line length")
    boat_description = models.TextField(verbose_name="Boat description", help_text="Please input boat water-line length")
    boat_mast_type = models.CharField(max_length=10, choices=CHOICES, default=SLOOP, verbose_name="Boat rigging type", help_text="Please input boat rigging type")
    boat_price = models.PositiveSmallIntegerField(default=0, verbose_name="price for the boat", help_text="Please input boat price")
    boat_country_of_origin = models.CharField(max_length=20, verbose_name="Boat country of origin", help_text="Please specify boat's country of origin")
    boat_sailboatdata_link = models.URLField(max_length=100, verbose_name="URL to Sailboatdata", help_text="Please type in URL to Sailboatdata page for this boat")
    boat_keel_type = models.CharField(max_length=50, verbose_name="Boat keel type", help_text="Please specify boat's keel type")
    boat_publish_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Boats primary data"
        verbose_name_plural = "Boats primary data"


class BoatImage(models.Model):
    boat_photo = models.ImageField(upload_to="photos/", verbose_name='Boat photo', help_text="Please attach any photo of the boat")
    boat = models.ForeignKey("BoatModel", null=True, on_delete=models.PROTECT, verbose_name="Boat")

    class Meta:
        verbose_name = "Boat photo"
        verbose_name_plural = "Boat photos"

#35  choices

