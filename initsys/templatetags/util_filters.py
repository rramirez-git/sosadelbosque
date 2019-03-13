from django import template
from django.template.defaultfilters import stringfilter
from random import randint

from initsys.models import Setting
from routines.utils import get_setting_fn, as_paragraph_fn

register = template.Library()


@register.filter
@stringfilter
def summary(text):
    number_of_words = 25
    if len(text.split(" ")) > number_of_words:
        return " ".join(text.split(" ")[: number_of_words]) + "..."
    return text


@register.filter
@stringfilter
def as_paragraph(text):
    return as_paragraph_fn(text)


@register.filter
def random_num(num_ini, num_fin):
    return "{:3d}".format(randint(num_ini, num_fin))


@register.filter
def money2display(num):
    return "{:0,.2f}".format(num)


@register.filter
@stringfilter
def get_setting(sectionvalue):
    """
    Obtiene el valor de un setting

    (string) sectionvalue   Setting a obtener en formato section.value

    return string
    """
    return get_setting_fn(sectionvalue, Setting)


@register.filter
def keyvalue(dict, key):
    data = ''
    try:
        data = dict[key]
    except:
        print("No se encontro la llave {} en {}".format(key,dict))
    return data


@register.filter
def ifNone(value, default=""):
    return value or default
