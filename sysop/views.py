from django.http import HttpResponse
from django.utils import simplejson
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

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
        simplejson.dumps(dict([
            r.serialize() for r in Rotate.objects.all()
        ])),
        content_type="application/json",
    )


@login_required
def own_servers(request):
    return render(request, 'sysop/index.html', {
        'own_servers':  Server.objects.filter(owner=request.user),
        'authorized_servers':  Server.objects.filter(authorized_sysops=request.user),
    })


@login_required
def all_servers(request):
    return render(request, 'sysop/index.html', {
        'all_servers':  Server.objects.exclude(deleted=True),
    })
