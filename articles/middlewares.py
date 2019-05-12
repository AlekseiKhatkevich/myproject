from .models import *
from django.db.models import Count, Subquery, OuterRef
from django.db.models.functions import TruncMinute

"""контекстный процессор помещает список подзаголовков в контекст и доп инфу для поиска и пагинации"""


def articles_context_processor(request):
    context = {}
    # время внесения самой последней статьи
    sq = Subquery(Article.objects.filter(foreignkey_to_subheading=OuterRef("pk")).order_by("-created_at").values("created_at")[:1])
    context["subheadings"] = SubHeading.objects.annotate(cnt=Count("article"), boat_num=Count(
        "one_to_one_to_boat"), newest=TruncMinute(sq)).prefetch_related("article_set").select_related("foreignkey",).all()

    context["keyword"] = ""
    context["all"] = ""
    if "keyword" in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            context['keyword'] = '?keyword=' + keyword
            context['all'] = context["keyword"]
    if "page" in request.GET:
        page = request.GET["page"]
        if page != "1" or 1:
            if context["all"]:
                context["all"] += '&page=' + page
            else:
                context["all"] = '?page=' + page
    return context


