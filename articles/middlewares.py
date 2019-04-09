from .models import *

"""контекстный процессор помещает список подзаголовков в контекст"""


def articles_context_processor(request):
    context = {}
    context["subheadings"] = SubHeading.objects.all()
    return context
