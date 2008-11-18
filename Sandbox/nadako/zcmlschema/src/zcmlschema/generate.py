import sys
from keyword import iskeyword
from xml.dom.minidom import getDOMImplementation

from zope.app.appsetup.appsetup import getConfigContext
from zope.configuration.docutils import makeDocStructures
from zope.schema import getFieldsInOrder

xsns = 'http://www.w3.org/2001/XMLSchema'

def quoteNS(ns):
    ns = ns.replace(':', '_co_')
    ns = ns.replace('/', '_sl_')
    return ns

def addDoc(doc, element, text):
    annotation = doc.createElement('xs:annotation')
    element.appendChild(annotation)
    documentation = doc.createElement('xs:documentation')
    annotation.appendChild(documentation)
    documentation.appendChild(doc.createTextNode(text))

def main():

    dom = getDOMImplementation()

    namespaces, subdirs = makeDocStructures(getConfigContext())
    common = namespaces.pop('', ())

    for ns, directives in namespaces.items():
        filename = quoteNS(ns) + '.xsd'
        file = open(filename, 'w')
        doc = dom.createDocument(xsns, 'xs:schema', None)
        root = doc.documentElement

        root.setAttribute('xmlns:xs', xsns)
        root.setAttribute('xs:targetNamespace', ns)

        directives.update(common)

        for directive in directives:
            el = doc.createElement('xs:element')
            el.setAttribute('name', directive)

            type = doc.createElement('xs:complexType')

            schema = directives[directive][0]

            if schema.__doc__:
                addDoc(doc, type, schema.__doc__)

            for name, field in getFieldsInOrder(schema):
                if name.endswith('_') and iskeyword(name[:-1]):
                    name = name[:-1]
                attr = doc.createElement('xs:attribute')
                attr.setAttribute('name', name)
                attr.setAttribute('type', 'string')

                if field.__doc__:
                    addDoc(doc, attr, field.__doc__)

                type.appendChild(attr)

            el.appendChild(type)
            root.appendChild(el)

        doc.writexml(file, addindent='\t', newl='\n')
