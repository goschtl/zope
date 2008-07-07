from lxml import etree
import martian
from classix.components import Element, XMLParser
from classix.directive import namespace, name, parser

def default_namespace(class_, module, parser, **data):
    return namespace.bind().get(parser)

def default_name(class_, module, parser, **data):
    return class_.__name__.lower()

class ElementGrokker(martian.ClassGrokker):
    martian.component(Element)

    martian.directive(parser)
    martian.directive(namespace, get_default=default_namespace)
    martian.directive(name, get_default=default_name)

    def execute(self, class_, parser, namespace, name, **kw):
        parser._lookup.add_element_class(namespace, name, class_)
        return True

class Lookup(etree.CustomElementClassLookup):
    def __init__(self):
        super(Lookup, self).__init__()
        self._classes = {}
        
    def add_element_class(self, namespace, name, class_):
        self._classes[(namespace, name)] = class_

    def lookup(self, node_type, document, namespace, name):
        return self._classes.get((namespace, name))

class XMLParserGrokker(martian.ClassGrokker):
    martian.component(XMLParser)
    martian.priority(martian.priority.bind().get(ElementGrokker) + 1)

    martian.directive(namespace)
    
    def execute(self, class_, **kw):
        class_._lookup = Lookup()
        return True
