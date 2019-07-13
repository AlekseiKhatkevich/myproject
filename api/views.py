from rest_framework import generics
from boats.models import BoatModel, BoatImage
from rest_framework.response import Response
from .serializers import BoatModelSerializer,  ExtraUserSerializer
from rest_framework import status
from rest_framework.decorators import api_view
from django.http import Http404
from rest_framework.views import APIView
from rest_framework import mixins
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models


@api_view(["GET", "POST"])
def boats_list(request, format=None):
    if request.method == "GET":
        data = BoatModel.objects.all()
        serializer = BoatModelSerializer(data, many=True)
        return Response(serializer.data)
    else:
        serializer = BoatModelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
def boat_detail(request, pk, format=None):
    try:
        boat = BoatModel.objects.get(pk=pk)
    except BoatModel.DoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    if request.method == "GET":
        serializer = BoatModelSerializer(boat)
        return Response(serializer.data)

    elif request.method == "PUT":

        serializer = BoatModelSerializer(boat, request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        boat.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BoatsList(generics.ListCreateAPIView):
    queryset = BoatModel.objects.all()
    serializer_class = BoatModelSerializer


class BoatDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = BoatModel.objects.all()
    serializer_class = BoatModelSerializer


class ExtraUserListView(generics.ListAPIView):
    pr = models.Prefetch("boatmodel_set", queryset=BoatModel.objects.all().only("pk",
                                                                                "author_id"))
    queryset = get_user_model().objects.all().prefetch_related(pr).only("id", "username",
                                                                        "first_name", "last_name")
    serializer_class = ExtraUserSerializer


class ExtraUserDetailView(generics.RetrieveAPIView):
    pr = models.Prefetch("boatmodel_set", queryset=BoatModel.objects.all().only("pk",
                                                                                "author_id"))
    queryset = get_user_model().objects.all().prefetch_related(pr).\
        only("id", "username", "first_name", "last_name", "email", "last_login", )
    serializer_class = ExtraUserSerializer
