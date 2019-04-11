from .models import *

"""контекстный процессор помещает список подзаголовков в контекст"""


def articles_context_processor(request):
    context = {}
    context["subheadings"] = SubHeading.objects.all()
    context["keyword"] = ""
    context["all"] = ""
    if "keyword" in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            context['keyword'] = '?keyword=' + keyword
            context['all'] = context["keyword"]
    if "page" in request.GET:
        page = request.GET["page"]
        if page != "1" or 1: # new
            if context["all"]:
                context["all"] += '&page=' + page
            else:
                context["all"] = '?page=' + page
    return context


