from .models import *

def boatimage_context_processor(request):
    context = {}
    context["bi"] = BoatImage.objects.all()
    return context
