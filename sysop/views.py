from django.http import HttpResponse
from django.utils import simplejson

from models import Rotate, Server


active = {'out_of_service': False, 'deleted': False}


def servers_json(request):
    return HttpResponse(
        simplejson.dumps(dict([
            s.serialize() for s in Server.objects.filter(**active)
        ])),
        content_type="application/json",
    )


def rotates_json(request):
    return HttpResponse(
        simplejson.dumps(dict([(
            r.dns_name,
            dict([s.serialize() for s in r.eligible.filter(**active)]),
        ) for r in Rotate.objects.all()])),
        content_type="application/json",
    )
