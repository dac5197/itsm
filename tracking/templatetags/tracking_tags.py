import json

from django import template

register = template.Library()

@register.filter
def loadJSON(data):
    return json.loads(data)