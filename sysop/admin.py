from models import *
from django.contrib import admin


class RotateInline(admin.TabularInline):
    model = Rotate.eligible.through


admin.site.register(Domain)


class ServerAdmin(admin.ModelAdmin):
    list_display = (
        'server_id',
        'fqdn',
        'owner',
        'ipv4',
        'ipv6',
        'out_of_service',
        'deleted',
    )
    list_filter = (
        'deleted',
        'out_of_service',
        'domain',
    )
    inlines = (RotateInline,)
admin.site.register(Server, ServerAdmin)


class RotateAdmin(admin.ModelAdmin):
    filter_horizontal = (
        'eligible',
    )
admin.site.register(Rotate, RotateAdmin)