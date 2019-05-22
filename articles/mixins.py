from django.views.generic import FormView, UpdateView
import json
from django.http import HttpResponseBadRequest
from django.shortcuts import HttpResponse


class AjaxFormMixin(FormView):

    def form_valid(self, form):
        form.save()
        return HttpResponse('OK')

    def form_invalid(self, form):
        errors_dict = json.dumps(dict([(k, [e for e in v]) for k, v in form.errors.items()]))
        return HttpResponseBadRequest(json.dumps(errors_dict))


class AjaxUpdateFormMixin(AjaxFormMixin, UpdateView):

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(AjaxFormMixin, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(AjaxFormMixin, self).post(request, *args, **kwargs)
