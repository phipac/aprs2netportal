from models import *
from django.contrib import admin
from django.db.models import Count


class RotateInline(admin.TabularInline):
    model = Rotate.eligible.through


admin.site.register(Domain)
admin.site.register(ReservedHostname)


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
        'rotate',
    )
    search_fields = ('server_id', 'hostname', 'ipv4', 'ipv6', 'owner__username')
    inlines = (RotateInline,)
admin.site.register(Server, ServerAdmin)


class RotateAdmin(admin.ModelAdmin):
    filter_horizontal = (
        'eligible',
    )
    list_display = ('__unicode__', 'name', 'server_count')

    def queryset(self, request):
        return Rotate.objects.annotate(server_count=Count('eligible'))

    def server_count(self, inst):
        return inst.server_count
    server_count.admin_order_field = 'server_count'
admin.site.register(Rotate, RotateAdmin)