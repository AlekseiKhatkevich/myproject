from rest_framework import serializers, validators
from boats.models import BoatModel, BoatImage
from articles.models import Comment
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.hashers import make_password
import datetime
from boats.signals import user_registrated
from smtplib import SMTPRecipientsRefused


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ("content", "created_at")


class BoatModelDetailSerializer(serializers.ModelSerializer):
    #  author = serializers.ReadOnlyField(source="author.username")
    #  https://medium.com/profil-software-blog/10-things-you-need-to-know-to-effectively-use
    #  -django-rest-framework-7db7728910e0
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    image = serializers.StringRelatedField(many=True, source="boatimage_set")
    comments = CommentSerializer(many=True, read_only=True, source="comment_set")

    default_error_messages = {**serializers.ModelSerializer.default_error_messages, **{
        'small_length': 'Boat length is way to small ({length} feats). Should be at least 10',
    }}

    class Meta:
        model = BoatModel
        exclude = ('boat_primary_photo', "change_date")
        current_year = datetime.datetime.now().year
        extra_kwargs = {
            "first_year": {'min_value': 1950, 'max_value': current_year},
            "last_year": {'min_value': 1950, 'max_value': current_year},
            "change_date": {'write_only': True},

        }

    def validate(self, data):
        first_year = data.get("first_year")
        last_year = data.get("last_year")
        if not all((first_year, last_year)):
            return data
        if first_year > last_year:
            raise serializers.ValidationError('last year should be greater then first '
                                                   'year')
        return data

    def validate_boat_length(self, value):
        if value < 10:
            self.fail("small_length", length=value)
        return value


class BoatModelListSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.username")

    class Meta:
        model = BoatModel
        fields = ("url", "id", "boat_name", "boat_length", "boat_mast_type", "author")


class ExtraUserSerializer(serializers.ModelSerializer):
    boats = serializers.SlugRelatedField(many=True, read_only=True, source="boatmodel_set",
                                         slug_field="boat_name")

    class Meta:
        model = get_user_model()
        fields = ("url", "username", "first_name", "last_name", "email", "last_login",
                  "boats", )
        validators = validators.UniqueTogetherValidator(
            queryset=get_user_model().objects.all().only("pk", "username", "first_name",
                                                         "last_name"),
            fields=("first_name", "last_name"))

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')
        if request is not None and not request.parser_context.get('kwargs'):
            fields.pop('email', None)
            fields.pop('last_login', None)
        return fields


class UserRegisterSerializer(serializers.ModelSerializer):
    """ Сериалайзер регистрации нового пользователя"""

    default_error_messages = {**serializers.ModelSerializer.default_error_messages, **
                {
                    'SMTP-error': "This email address - {email} isn't correct one"
                 }}

    class Meta:
        model = get_user_model()
        fields = ("password", "username", "first_name", "last_name", "email")
        extra_kwargs = {
            "password": {"write_only": True, "required": True},
            "username": {"min_length": 3}
        }

    @staticmethod
    def validate_password(value):
        #  Валидируем пароль и делаем с него хаш
        password_validation.validate_password(value)
        return make_password(value)

    def create(self, validated_data):
        validated_data.update({"is_active": False, "is_activated": False})
        user = serializers.ModelSerializer.create(self, validated_data)
        try:
            user_registrated.send(UserRegisterSerializer, instance=user)
        except SMTPRecipientsRefused:
            self.fail("SMTP-error", email=validated_data.get("email"))
        return user


