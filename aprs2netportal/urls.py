from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^sysop/', include('sysop.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^APRServe2.txt$', 'sysop.views.server_list'),
)
