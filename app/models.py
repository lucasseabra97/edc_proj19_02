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

@register.filter(name='uri_id')
def uri_id(uri):
    '''Returns the given wikidata id from a uri.'''
    return uri.split('/')[-1]

@register.filter(name='get')
def get(array, index):
    '''Returns the given wikidata id from a uri.'''
    return array[index]