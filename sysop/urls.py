from django.conf.urls import patterns, url

from sysop import views


urlpatterns = patterns('',
    url(r'^$', views.own_servers),
    url(r'^all$', views.all_servers),
    url(r'^servers.json$', views.servers_json, name='servers'),
    url(r'^rotates.json$', views.rotates_json, name='rotates'),
)