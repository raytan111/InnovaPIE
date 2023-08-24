from django import template

register = template.Library()

@register.filter(name='format_clp')
def format_clp(value):
    return "{:,}".format(value).replace(',', '.')
