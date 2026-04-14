import os
from django import template

register = template.Library()

@register.filter(name='filename')
def filename(value):
    if value:
        return os.path.basename(str(value))
    return ''
