import grok
from grok.interfaces import IContainer
from grokcore.component import Context
from grok.interfaces import IContainer

import megrok.rdf

import rdflib

# This dictionary is used by the rdf.type directive
# to map rdf types to rdfmodel classes
rdftype_registry = {}

class ns(object):
    rdf = rdflib.Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    zope = rdflib.Namespace("http://namespaces.zope.org/rdf#")

def getModel(node):
    graph = grok.getSite().graph
    type = list(graph.objects(node, ns.rdf['type']))[0]
    return rdftype_registry[unicode(type)](node)

class Model(Context):
    def __init__(self, subject):
        self.subject = subject

class MultiProperty(object):

    def __init__(self, predicate):
        self.predicate = predicate

    def __get__(self, instance, type):
        result = []
        graph = grok.getSite().graph
        for object in graph.objects(instance.subject, self.predicate):
            if isinstance(object, rdflib.Literal):
                result.append(unicode(object))
            else:
                result.append(getModel(object))
        return result

class Container(object):

    grok.implements(IContainer)

    def __init__(self, subject, predicate):
        self.subject = subject
        self.predicate = predicate
        self.key = megrok.rdf.key.bind().get(self)

    def keys(self):
        graph = grok.getSite().graph
        for object in graph.objects(self.subject,
                                    self.predicate):
            for name in graph.objects(object, self.key):
                yield unicode(name)
                break

    def values(self):
        graph = grok.getSite().graph
        for object in graph.objects(self.subject, self.predicate):
            yield getModel(object)

    def items(self):
        graph = grok.getSite().graph
        for object in graph.objects(self.subject,
                                    self.predicate):
            for name in graph.objects(object, self.key):
                yield (unicode(name), getModel(object))
                break

    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def __getitem__(self, key):
        graph = grok.getSite().graph
        for object in graph.objects(self.subject,
                                    self.predicate):
            for name in graph.objects(object, self.key):
                if unicode(name) == key:
                    return getModel(object)
        raise KeyError

class ContainerProperty(MultiProperty):

    def __init__(self, predicate, container_class):
        self.predicate = predicate
        self.container_class = container_class

    def __get__(self, instance, type):
        return self.container_class(instance.subject,
                                   self.predicate)

class Property(MultiProperty):
    def __get__(self, instance, type):
        result = super(Property, self).__get__(instance, type)
        if not len(result):
            return None
        return result[0]


