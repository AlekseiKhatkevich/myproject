from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .forms import ContactForm
from django.views import View


#FBV


def contactPage(request):
    form = ContactForm()
    return render(request, "testapp/contact.html", {"contactForm": form})


def postContact(request):
    if request.method == "POST" and request.is_ajax():
        form = ContactForm(request.POST)
        form.save()
        return JsonResponse({"success": True}, status=200)
    return JsonResponse({"success": False}, status=400)


class ContactAjax(  View):
    form_class = ContactForm
    template_name = "testapp/contact.html"

    def get(self, *args, **kwargs):
        form = self.form_class()
        return render(self.request, self.template_name, {"contactForm": form})

    def post(self, *args, **kwargs):

        if self.request.method == "POST" and self.request.is_ajax():
            form = self.form_class(self.request.POST)
            form.save()
            return JsonResponse({"success": True}, status=200)
        else:
            if self.request.is_ajax():
                return JsonResponse({"NO success": "  ajax"},  status=400, safe=False)
            else:
                return  JsonResponse({"NO success": " no ajax"},  status=400, safe=False)

