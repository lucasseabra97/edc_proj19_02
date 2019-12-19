from django.db import models

from django.template.defaultfilters import register

@register.filter(name='dict_value')
def dict_value(d, k):
    '''Returns the given key from a dictionary.'''
    if k in d:
        return d[k]['value']
    return ''

@register.filter(name='dict_type')
def dict_type(d, k):
    '''Returns the given key from a dictionary.'''
    if k in d:
        return d[k]['type']
    return ''