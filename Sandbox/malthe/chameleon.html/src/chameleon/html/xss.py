from cssutils.parse import CSSParser
import chameleon.core.config

class Element(object):
    def __init__(self, selector, namespaces, name="",
                 attributes=None, structure=False, mode='content', **kwargs):
        if kwargs:
            for name in kwargs:
                raise ValueError("Unknown property: %s" % repr(name))
        self.namespaces = namespaces
        self.selector = selector
        self.name = name
        self.mode = mode
        self.attributes = attributes
        self.structure = structure

namespace = 'xmlns'
namespaces = {namespace: chameleon.core.config.XHTML_NS}

def parse_xss(stream):
    elements = []

    parser = CSSParser(loglevel=0)
    for rule in parser.parseFile(stream):
        # ignore comments,
        if rule.type == -1:
            continue
        
        properties = {}
        for prop in rule.style:
            properties[str(prop.name)] = prop.value

        for selector in rule.selectorList:
            selectors = []
            for item in selector.seq:
                if item.type == 'type-selector':
                    extra, name = item.value
                    selectors.append('%s|%s' % (namespace, name))
                else:
                    selectors.append(item.value)
            selector = "".join(selectors)
            element = Element(
                selector,
                namespaces,
                **properties)

        elements.append(element)

    return elements
