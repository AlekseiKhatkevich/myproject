from boats.models import BoatModel, BoatImage
from rest_framework.response import Response
from api import serializers
from rest_framework import status, permissions, generics, renderers, viewsets
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from django.contrib.auth import get_user_model
from django.db import models
from .permissions import IsOwnerOrFuckOff
from rest_framework.views import APIView
from rest_framework.permissions import SAFE_METHODS
from rest_framework_extensions.cache.mixins import CacheResponseMixin
from django.utils.decorators import method_decorator


class ExtraUserViewSet(viewsets.ReadOnlyModelViewSet):
    pr = models.Prefetch("boatmodel_set", queryset=BoatModel.objects.all().only("pk",
                                                                                "author_id"))
    queryset = get_user_model().objects.all().prefetch_related(pr). \
        only("id", "username", "first_name", "last_name", "email", "last_login", )
    #serializer_class = ExtraUserSerializer


class BoatviewSet(viewsets.ModelViewSet):
    pr = models.Prefetch("boatimage_set", queryset=BoatImage.objects.all().only("pk",
                                                                                "boat_id"))
    queryset = BoatModel.objects.select_related("author").prefetch_related(pr).all()
    #serializer_class = BoatModelSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrFuckOff)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

##############################################################################################


class BoatsListView(generics.ListCreateAPIView):
    queryset = BoatModel.objects.all().only("pk", "boat_name", "boat_length", "author_id",
                                            "boat_mast_type", "author")
    serializer_class = serializers.BoatModelDetailSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrFuckOff)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer(self, *args, **kwargs):
        if self.request.method in SAFE_METHODS:
            serializer_class = serializers.BoatModelListSerializer
        else:
            serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)


class BoatDetailView(generics.RetrieveUpdateDestroyAPIView):
    pr = models.Prefetch("boatimage_set", queryset=BoatImage.objects.all().only("pk",
                                                                                "boat_id"))
    queryset = BoatModel.objects.select_related("author").prefetch_related(pr).all()
    serializer_class = serializers.BoatModelDetailSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrFuckOff)


class ExtraUserListView(generics.ListAPIView):
    pr = models.Prefetch("boatmodel_set", queryset=BoatModel.objects.all().only("pk",
                                                                                "author_id"))
    queryset = get_user_model().objects.all().prefetch_related(pr).only("id", "username",
                                                                "first_name", "last_name")
    serializer_class = serializers.ExtraUserSerializer


class ExtraUserDetailView(generics.RetrieveAPIView):
    pr = models.Prefetch("boatmodel_set", queryset=BoatModel.objects.all().only("pk",
                                                                                "author_id"))
    queryset = get_user_model().objects.all().prefetch_related(pr).\
        only("id", "username", "first_name", "last_name", "email", "last_login", )
    serializer_class = serializers.ExtraUserSerializer


@api_view(("GET",))
def api_root(request, format=None):
    return Response({
        "users": reverse("extrauser-list", request=request, format=format),
        "boats": reverse("boatmodel-list", request=request, format=format)
    })


