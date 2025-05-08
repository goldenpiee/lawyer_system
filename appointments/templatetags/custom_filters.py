import os
from django import template

register = template.Library()

@register.filter(name='filename')
def filename(value):
    """
    Извлекает имя файла из полного пути.
    Например: "documents/some_file.pdf" -> "some_file.pdf"
    """
    if value:
        return os.path.basename(str(value))
    return ''
