from django import template

register = template.Library()

@register.filter(name='split')
def split(value, key=','):
    """Returns the value split by key"""
    return [v.strip() for v in value.split(key)]
