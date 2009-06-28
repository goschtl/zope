try:
    import json # Python v2.6
except ImportError:
    import simplejson as json

import grokcore.component as grok
import zope.datetime
from persistent import Persistent
from zope.interface import Interface, alsoProvides
from zope.location import Location
from zope.schema import getFieldsInOrder
from zope.schema.interfaces import IText, IInt, IObject, IList, IChoice, ISet
from zope.schema.interfaces import IDatetime

def serialize_to_tree(container, schema, instance):
    for name, field in getFieldsInOrder(schema):
        value = field.get(instance)
        container[name] = IJSONGenerator(field).output(value)

def serialize(schema, instance, encoding='UTF-8',
              pretty_print=True):
    json_dict = {}
    serialize_to_tree(json_dict, schema, instance)
    if pretty_print:
        indent = 2
    else:
        indent = None
    return json.dumps(json_dict, sort_keys=True, indent=indent)

def deserialize_from_dict(container, schema, instance):
    for key, value in container.iteritems():
        field = schema[key]
        value = IJSONGenerator(field).input(value)
        field.set(instance, value)
    
    alsoProvides(instance, schema)

def deserialize(JSON, schema, instance):
    obj_dict = json.loads(JSON)
    deserialize_from_dict(obj_dict, schema, instance)

class GeneratedObject(Location, Persistent):
    def __init__(self):
        pass

class IJSONGenerator(Interface):

    def output(value):
        """Output value as JSON item according to field.
        """

    def input(item):
        """Input JSON item according to field and return value.
        """

class Text(grok.Adapter):
    grok.context(IText)
    grok.implements(IJSONGenerator)

    def output(self, value):
        return value

    def input(self, item):
        if item is not None:
            return unicode(item)
        return None

class Int(grok.Adapter):
    grok.context(IInt)
    grok.implements(IJSONGenerator)

    def output(self, value):
        return value

    def input(self, item):
        return item

class Object(grok.Adapter):
    grok.context(IObject)
    grok.implements(IJSONGenerator)

    def output(self, value):
        cd = {}
        for name, field in getFieldsInOrder(self.context.schema):
            cd[name] = IJSONGenerator(field).output(field.get(value))
        return cd

    def input(self, item):
        instance = GeneratedObject()
        deserialize_from_dict(item, self.context.schema, instance)
        return instance

class List(grok.Adapter):
    grok.context(IList)
    grok.implements(IJSONGenerator)

    def output(self, value):
        lst = []
        field = self.context.value_type
        for v in value:
            lst.append(IJSONGenerator(field).output(v))
        return lst

    def input(self, item):
        field = self.context.value_type
        if item is None:
            return []
        return [
            IJSONGenerator(field).input(sub_item)
            for sub_item in item]

class Datetime(grok.Adapter):
    grok.context(IDatetime)
    grok.implements(IJSONGenerator)

    def output(self, value):
        if value is None:
            return None
        else:
            return value.strftime('%Y-%m-%dT%H:%M:%S')

    def input(self, item):
        if item is not None:
            return zope.datetime.parseDatetimetz(item)
        return None

class Choice(grok.Adapter):
    grok.context(IChoice)
    grok.implements(IJSONGenerator)
    
    def output(self, value):
        return value

    def input(self, item):
        if item is not None:
            return item
        return None

# Remember, sets cannot store non-hashables.
class Set(grok.Adapter):
    grok.context(ISet)
    grok.implements(IJSONGenerator)

    def output(self, value):
        lst = []
        field = self.context.value_type
        for v in value:
            lst.append(IJSONGenerator(field).output(v))
        return lst

    def input(self, item):
        field = self.context.value_type
        if item is None:
            return set()
        return set([
            IJSONGenerator(field).input(sub_item)
            for sub_item in item])
