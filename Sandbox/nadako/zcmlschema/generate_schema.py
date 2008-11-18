import sys
from keyword import iskeyword
from xml.dom.minidom import getDOMImplementation

from zope.app.appsetup.appsetup import getConfigContext
from zope.configuration.docutils import makeDocStructures
from zope.schema import getFieldsInOrder

namespaces, subdirs = makeDocStructures(getConfigContext())
dom = getDOMImplementation()

def quoteNS(ns):
    ns = ns.replace(':', '_co_')
    ns = ns.replace('/', '_sl_')
    return ns

seenDirectives = set()

def addDoc(doc, element, text):
    annotation = doc.createElement('annotation')
    element.appendChild(annotation)
    documentation = doc.createElement('documentation')
    annotation.appendChild(documentation)
    documentation.appendChild(doc.createTextNode(text))

for ns, directives in namespaces.items():
    if not ns:
        ns = 'all'
    filename = quoteNS(ns) + '.xsd'
    file = open(filename, 'w')
    doc = dom.createDocument('http://www.w3.org/2001/XMLSchema', 'schema', None)
    root = doc.documentElement

    root.setAttribute('xmlns', 'http://www.w3.org/2001/XMLSchema')
    root.setAttribute('targetNamespace', ns)
    root.setAttribute('xmlns:target', ns)

    for directive in directives:
        schema = directives[directive][0]
        type_name = '%s.%s' % (schema.__module__, schema.__name__)

        if type_name not in seenDirectives:
            type = doc.createElement('complexType')
            type.setAttribute('name', type_name)
            
            if schema.__doc__:
                addDoc(doc, type, schema.__doc__)
            
            for name, field in getFieldsInOrder(schema):
                if name.endswith('_') and iskeyword(name[:-1]):
                    name = name[:-1]
                attr = doc.createElement('attribute')
                attr.setAttribute('name', name)
                attr.setAttribute('type', 'string')

                if field.__doc__:
                    addDoc(doc, attr, field.__doc__)

                type.appendChild(attr)
            root.appendChild(type)
            seenDirectives.add(type_name)

        el = doc.createElement('element')
        el.setAttribute('name', directive)
        el.setAttribute('type', 'target:' + type_name)
        root.appendChild(el)

    doc.writexml(file, addindent='\t', newl='\n')
