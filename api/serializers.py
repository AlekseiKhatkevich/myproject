from rest_framework import serializers
from articles.models import Heading, UpperHeading, SubHeading, Article, Comment
from boats.models import BoatModel
from django.contrib.auth import get_user_model


class UpperHeadingSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=20, required=True, allow_blank=False)
    order = serializers.IntegerField()
    subheading_set = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    def create(self, validated_data):
        return UpperHeading.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", "instance.name")
        instance.order = validated_data.get("order", "instance.order")
        instance.save()
        return instance

    class Meta:
        model = UpperHeading
        fields = ("id", "name", "order", "subheading_set")


class SubHeadingSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=20, required=True, allow_blank=False)
    order = serializers.IntegerField()
    #one_to_one_to_boat

    class Meta:
        model = SubHeading
        fields = ("id", "name", "order", )


class BoatSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    #author =
    boat_name = serializers.CharField(required=True,  max_length=20)
    boat_length = serializers.FloatField(required=True)
    boat_description = serializers.CharField(required=False, allow_blank=True)
    boat_mast_type = serializers.ChoiceField(required=True, choices=BoatModel.CHOICES)
    boat_price = serializers.IntegerField(required=True)
    #boat_country_of_origin =
    boat_sailboatdata_link = serializers.URLField(required=True)
    boat_keel_type = serializers.CharField(required=True, max_length=50)
    boat_publish_date = serializers.DateTimeField(required=False, read_only=True)
    first_year = serializers.IntegerField(required=True)
    last_year = serializers.IntegerField(required=True)


class BoatModelSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.username")

    class Meta:
        model = BoatModel
        fields = ("id", "boat_name", "boat_length", "boat_description", "boat_mast_type",
                  "boat_price", "boat_sailboatdata_link", "boat_keel_type",
                  "boat_publish_date", "first_year", "last_year", "author",
                  "boat_country_of_origin")


class ExtraUserSerializer(serializers.ModelSerializer):
    boats = serializers.PrimaryKeyRelatedField(many=True, queryset=get_user_model().
                                               objects.all(), source="boatmodel_set")

    class Meta:
        model = get_user_model()
        fields = ("username", "first_name", "last_name", "email", "last_login", "boats")

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')
        if request is not None and not request.parser_context.get('kwargs'):
            fields.pop('email', None)
            fields.pop('last_login', None)
        return fields
