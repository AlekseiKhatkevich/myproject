from boats.models import BoatModel, BoatImage
from rest_framework.response import Response
from .serializers import BoatModelSerializer,  ExtraUserSerializer
from rest_framework import status, permissions, generics, renderers
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from django.contrib.auth import get_user_model
from django.db import models
from .permissions import IsOwnerOrFuckOff


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
    queryset = BoatModel.objects.raw(" SELECT  id, author_id,boat_name,"
                                                              "boat_length,"
                                     "boat_description,boat_mast_type,boat_price,"
                                     "boat_country_of_origin,boat_sailboatdata_link,"
                                     "boat_keel_type,boat_publish_date,boat_primary_photo,"
                                     "first_year,last_year,change_date FROM "
                                     "boats_boatmodel")
    serializer_class = BoatModelSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrFuckOff)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class BoatDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = BoatModel.objects.select_related("author").all()
    serializer_class = BoatModelSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrFuckOff)


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


@api_view(("GET",))
def api_root(request, format=None):
    return Response({
        "users": reverse("api:extrauser-list", request=request, format=format),
        "boats": reverse("api:boats-list", request=request, format=format)
    })


class BoatHighlight(generics.GenericAPIView):
    queryset = BoatModel.objects.all()
    renderer_classes = (renderers.StaticHTMLRenderer, )

    def get(self, request, *args, **kwargs):
        boat = self.get_object()
        return Response(boat.highlighted)
