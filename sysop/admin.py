from models import *
from django.contrib import admin


class RotateInline(admin.TabularInline):
    model = Rotate.eligible.through


class ServerAdmin(admin.ModelAdmin):
    list_display = (
        '__unicode__',
        'dns_name',
        'owner',
        'ipv4',
        'ipv6',
        'out_of_service',
        'deleted',
    )
    list_filter = (
        'deleted',
        'out_of_service',
    )
    inlines = (RotateInline,)
admin.site.register(Server, ServerAdmin)


admin.site.register(Rotate)