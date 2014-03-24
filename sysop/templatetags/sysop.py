from django import template
from django.core import urlresolvers


register = template.Library()


@register.inclusion_tag('sysop/servertable.html', takes_context=True)
def servertable(context, servers, **kwargs):
    kwargs['servers'] = servers
    return kwargs
