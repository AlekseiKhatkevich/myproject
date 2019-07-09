from rest_framework import generics
from articles.models import Heading, UpperHeading, SubHeading, Article, Comment
from boats.models import BoatModel, BoatImage
from rest_framework.response import Response
from .serializers import UpperHeadingSerializer, SubHeadingSerializer, BoatModelSerializer, BoatSerializer
from rest_framework import status
from rest_framework.decorators import api_view
from django.http import Http404
from rest_framework.views import APIView
from rest_framework import mixins


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


class BoatsList(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    queryset = BoatModel.objects.all()
    serializer_class = BoatModelSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class BoatDetail(APIView):

    def get_object(self, pk):
        try:
            return BoatModel.objects.get(pk=pk)
        except BoatModel.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        boat = self.get_object(pk)
        serializer = BoatModelSerializer(boat)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        boat = self.get_object(pk)
        serializer = BoatModelSerializer(boat, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        boat = self.get_object(pk)
        boat.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

