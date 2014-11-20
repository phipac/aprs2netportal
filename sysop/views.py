from functools import wraps
import json

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import available_attrs, cache_page, never_cache

from models import Rotate, Server
from forms import SysopServerForm, UserForm


def cache_page_vary_authenticated(timeout):
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            return cache_page(timeout, key_prefix="_auth_%s_" % request.user.is_authenticated())(view_func)(request, *args, **kwargs)
        return _wrapped_view
    return decorator


# cache rendered page on server, but send cache-control no-cache to client
@never_cache
@cache_page_vary_authenticated(60 * 30)
def servers_json(request):
    return HttpResponse(
        json.dumps(dict([
            s.serialize(with_email=request.user.is_authenticated()) for s in Server.objects.all()
        ])),
        content_type="application/json",
    )


@never_cache
@cache_page(60 * 30)
def rotates_json(request):
    return HttpResponse(
        json.dumps(dict([
            r.serialize() for r in Rotate.objects.all()
        ])),
        content_type="application/json",
    )


@never_cache
@cache_page(60 * 30)
def server_list(request):
    aprs2_servers = Rotate.objects.get(
        hostname='rotate', domain__domain='aprs2.net').eligible
    #TODO: support UTF-8 for server locations
    return render(request, 'sysop/APRServe2.txt', {
        'rotates': Rotate.objects.filter(regional=True),
        'servers': aprs2_servers.exclude(deleted=True).order_by('hostname')
    }, content_type="text/plain")


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


@login_required
def server_detail(request, server_id):
    server = Server.objects.get(id=server_id)
    form = SysopServerForm(instance=server)

    if server.owner == request.user \
    or request.user in server.authorized_sysops.all():
        can_edit = True
        if request.method == "POST":
            form = SysopServerForm(request.POST, instance=server)
            if form.is_valid():
                form.save()
                messages.success(request, '%s saved.' % server)
                return HttpResponseRedirect('/sysop/')
            else:
                messages.warning(request, 'Form validation error. Details below.')
    else:
        can_edit = False

    return render(request, 'sysop/edit_server.html', {
        'server': server,
        'form': form,
        'can_edit': can_edit,
    })


@login_required
def user_detail(request):
    if request.method == "POST":
        form = UserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'User settings saved.')
            return HttpResponseRedirect('/sysop/')
        else:
            messages.warning(request, 'Form validation error. Details below.')
    else:
        form = UserForm(instance=request.user)

    return render(request, 'registration/profile.html', {
        'form': form,
    })
