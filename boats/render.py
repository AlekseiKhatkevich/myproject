from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
import xhtml2pdf.pisa as pisa
from myproject import settings
import os


def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    # use short variable names
    sUrl = settings.STATIC_URL      # Typically /static/
    sRoot = settings.STATIC_ROOT    # Typically /home/userX/project_static/
    mUrl = settings.MEDIA_URL       # Typically /static/media/
    mRoot = settings.MEDIA_ROOT     # Typically /home/userX/project_static/media/

    # convert URIs to absolute system paths
    if uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, ""))
    elif uri.startswith(sUrl):
        path = os.path.join(sRoot, uri.replace(sUrl, ""))
    else:
        return uri  # handle absolute uri (ie: http://some.tld/foo.png)

    # make sure that file exists
    if not os.path.isfile(path):
            raise Exception(
                'media URI must start with %s or %s' % (sUrl, mUrl)
            )
    return path


"""Рендеринг ПДФ в поток(остальная часть во вьюхах)"""


class Render:  # https://codeburst.io/django-render-html-to-pdf-41a2b9c41d16

    @staticmethod
    def render(template_path: str, params: dict, filename: str):
        template = get_template(template_path)
        html = template.render(params)
        response = BytesIO()  # python.pdf str 442
        pdf = pisa.CreatePDF(BytesIO(html.encode("UTF-8")), response, encoding="UTF-8",
                             link_callback=link_callback)
        if not pdf.err:
            resp = HttpResponse(response.getvalue(), content_type='application/pdf')
            resp['Content-Disposition'] = 'filename="%s"' % (filename + ".pdf")
            return resp
        else:
            return HttpResponse("Error Rendering PDF", status=400)

