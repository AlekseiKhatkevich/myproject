from boats.models import BoatModel, BoatImage
from rest_framework.response import Response
from api import serializers
from rest_framework import status, permissions, generics,  viewsets, mixins, views
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework.serializers import ValidationError
from django.contrib.auth import get_user_model
from django.db import models, connection
from .permissions import IsOwnerOrFuckOff
from rest_framework.permissions import SAFE_METHODS
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
import more_itertools
from .models import UniqueWordsTriGramm
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity, TrigramDistance


class ExtraUserViewSet(viewsets.ReadOnlyModelViewSet):
    pr = models.Prefetch("boatmodel_set", queryset=BoatModel.objects.all().only("pk",
                                                                                "author_id"))
    queryset = get_user_model().objects.all().prefetch_related(pr). \
        only("id", "username", "first_name", "last_name", "email", "last_login", )


class BoatviewSet(viewsets.ModelViewSet):
    pr = models.Prefetch("boatimage_set", queryset=BoatImage.objects.all().only("pk",
                                                                                "boat_id"))
    queryset = BoatModel.objects.select_related("author").prefetch_related(pr).all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrFuckOff)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

##############################################################################################


class BoatsListView(generics.ListCreateAPIView):
    """Список лодок"""
    queryset = BoatModel.objects.all().only("pk", "boat_name", "boat_length", "author_id",
                                            "boat_mast_type", "author")
    serializer_class = serializers.BoatModelDetailSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrFuckOff)

    #def perform_create(self, serializer):
        #serializer.save(author=self.request.user)

    def get_serializer(self, *args, **kwargs):
        if self.request.method in SAFE_METHODS:
            serializer_class = serializers.BoatModelListSerializer
        else:
            serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)


class BoatDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Отдельная лодка"""
    pr = models.Prefetch("boatimage_set", queryset=BoatImage.objects.all().only("pk",
                                                                                "boat_id"))
    queryset = BoatModel.objects.select_related("author").prefetch_related(pr).all()
    serializer_class = serializers.BoatModelDetailSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrFuckOff)


class ExtraUserListView(generics.ListAPIView):
    """Список пользователей"""
    pr = models.Prefetch("boatmodel_set", queryset=BoatModel.objects.all().only("pk",
                                                                                "author_id"))
    queryset = get_user_model().objects.all().prefetch_related(pr).only("id", "username",
                                                                "first_name", "last_name")
    serializer_class = serializers.ExtraUserSerializer


class ExtraUserDetailView(generics.RetrieveAPIView):
    """Отдельный пользователь"""
    pr = models.Prefetch("boatmodel_set", queryset=BoatModel.objects.all().only("pk",
                                                                                "author_id"))
    queryset = get_user_model().objects.all().prefetch_related(pr).\
        only("id", "username", "first_name", "last_name", "email", "last_login", )
    serializer_class = serializers.ExtraUserSerializer


@api_view(("GET",))
def api_root(request, format=None):
    """АПИ рут"""
    return Response({
        "users": reverse("extrauser-list", request=request, format=format),
        "boats": reverse("boatmodel-list", request=request, format=format),
        "schema": reverse("schema", request=request, format=format),
    })


class UserRegistrationView(mixins.DestroyModelMixin, generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    lookup_field = ("username", )
    serializer_class = serializers.UserRegisterSerializer

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def get_object(self):
        try:
            obj = self.queryset.get(username=self.request.data.get("username", None))
        except ObjectDoesNotExist:
            raise Http404
        return obj

    def perform_destroy(self, instance):
        mark = self.request.query_params.get("mark")
        if mark == "True":
            instance.delete()
        elif mark == "False":
            instance.is_active = instance.is_activated = False
            instance.save()
        else:
            raise ValidationError("Please provide marks in range(True, False)")


class UserProfileView(views.APIView):  # http://127.0.0.1:8000/api/users/profile/1/

    def get(self, request, format=None, **kwargs):
        user = self.request.user
        serializer = serializers.UserProfileSrializer(user)
        data = serializer.data
        return Response(data)


@method_decorator(sensitive_post_parameters(), name="dispatch")
class UserLoginView(generics.GenericAPIView):
    serializer_class = serializers.LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_202_ACCEPTED)


class ProductSearchListView(generics.ListAPIView):
    serializer_class = serializers.ProductSearchSerializer
    model = serializer_class.Meta.model
    db_table = model._meta.db_table
    fields = [f.name for f in model._meta.get_fields(include_parents=False)]
    analyzers_list = model.get_list_of_analyzers()

    def dict_of_keywords(self):
        keywords = {f: self.request.query_params.get(f, None)
                    for f in self.fields
                    if self.request.query_params.get(f, None) is not None
                            }
        return keywords

    def get_queryset(self):
        if not self.dict_of_keywords():
            return self.model.objects.all()
        else:
            keyword = self.dict_of_keywords().get(
                more_itertools.one(self.dict_of_keywords().keys())
            )
            qs = self.model.objects.raw(
                """
                SELECT *,
                ts_rank_cd(to_tsvector('english', description),
                to_tsquery(%(analyzer)s, %(keyword)s), 32) as rnk 
                FROM api_product 
                WHERE to_tsvector(%(analyzer)s, description) @@ 
                to_tsquery(%(analyzer)s, %(keyword)s)
                ORDER BY rnk DESC, id 
                """
                ,
                params={
                    'keyword': keyword,
                    'db_table': self.db_table,
                    'analyzer': 'english'
                }
            )

            return qs

    def get_paginated_response(self, data):
        return generics.ListAPIView.get_paginated_response(self, self.analyzers_list + data)


class SuggestionView(views.APIView):
    serializer_class = serializers.SuggestionSerializer
    model = serializer_class.Meta.model
    db_table = model._meta.db_table
    lookup_field = 'word'
    lookup_url_kwarg = lookup_field

    def get(self, request, format=None, **kwargs):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT word FROM ts_stat(
                'SELECT to_tsvector(''simple'', description)
                FROM api_product');
                """,
                # [source, ]
            )
        return Response()

    # def get(self, request, format=None, **kwargs):
    #     user = self.request.user
    #     serializer = serializers.UserProfileSrializer(user)
    #     data = serializer.data
    #     return Response(data)
