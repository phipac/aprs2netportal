from django.http import HttpResponse
from django.utils import simplejson

from models import Rotate, Server


def servers_json(request):
    return HttpResponse(
        simplejson.dumps(dict([
            s.serialize() for s in Server.objects.all()
        ])),
        content_type="application/json",
    )


def rotates_json(request):
    return HttpResponse(
        simplejson.dumps(dict([(
            r.dns_name,
            dict([s.serialize() for s in r.eligible.all()]),
        ) for r in Rotate.objects.all()])),
        content_type="application/json",
    )
