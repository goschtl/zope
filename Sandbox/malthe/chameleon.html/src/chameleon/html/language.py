import cgi
import os

from chameleon.core import translation
from chameleon.core import config
from chameleon.core import etree
from chameleon.core import types
from chameleon.core import utils

true_values = 'true', '1', 'yes'

from xss import parse_xss

import lxml.cssselect

def merge_dicts(dict1, dict2):
    if dict2 is None:
        return dict1
    
    keys = set(dict1).union(set(dict2))

    for key in keys:
        if key == 'class':
            value1 = dict1.get(key)
            value2 = dict2.get(key)

            if value1 is not None:
                if value2 is not None:
                    dict1[key] += " " + value2
            elif value2 is not None:
                dict1[key] = value2
        else:
            value2 = dict2.get(key)
            if value2 is not None:
                dict1[key] = value2
    return dict1
    
def composite_attr_dict(attrib, *dicts):
    return reduce(merge_dicts, (dict(attrib),) + dicts)

class Element(translation.Element):
    """The XSS template language base element."""
    
    class node(translation.Node):
        define_symbol = '_define'
        composite_attr_symbol = '_composite_attr'
        
        @property
        def omit(self):
            return self.element.xss_omit.lower() in true_values

        @property
        def dict_attributes(self):
            if self.element.xss_attributes is not None:
                xhtml_attributes = utils.get_attributes_from_namespace(
                    self.element, config.XHTML_NS)
                attrib = repr(tuple(xhtml_attributes.items()))

                names = self.element.xss_attributes.split(',')
                attributes = ", ".join(
                    ["attributes.get('%s')" % name.strip() for name in names])
                
                value = types.value(
                    "%s(%s, %s)" % \
                    (self.composite_attr_symbol, attrib, attributes))
                value.symbol_mapping[self.composite_attr_symbol] = composite_attr_dict
                return value
            
        @property
        def define(self):
            content = self.element.xss_content
            if content is not None:
                expression = types.value(
                    "content.get('%s')" % content)
                return types.definitions((
                    (types.declaration((self.define_symbol,)), types.parts((expression,))),))
            
        @property
        def content(self):
            content = self.element.xss_content
            if content is not None:
                expression = types.value(
                    "%s or %s" % (self.define_symbol, repr(self.element.text)))

                if self.element.xss_structure.lower() not in true_values:
                    expression = types.escape((expression,))

                return expression

        @property
        def skip(self):
            if self.element.xss_content is not None:
                return types.value(self.define_symbol)
                
    node = property(node)

    xss_omit = utils.attribute(
        '{http://namespaces.repoze.org/xss}omit', default="")
    
    xss_content = utils.attribute(
        '{http://namespaces.repoze.org/xss}content')

    xss_structure = utils.attribute(
        '{http://namespaces.repoze.org/xss}structure', default="")

    xss_attributes = utils.attribute(
        '{http://namespaces.repoze.org/xss}attributes')

class XSSTemplateParser(etree.Parser):
    """XSS template parser."""
    
    element_mapping = {
        config.XHTML_NS: {None: Element},
        config.META_NS: {None: translation.MetaElement}}

class DynamicHTMLParser(XSSTemplateParser):    
    def __init__(self, filename):
        self.path = os.path.dirname(filename)
        
    def parse(self, body):
        root, doctype = super(DynamicHTMLParser, self).parse(body)

        # locate XSS links
        links = root.xpath(
            './/xmlns:link[@rel="xss"]', namespaces={'xmlns': config.XHTML_NS})
        for link in links:
            try:
                href = link.attrib['href']
            except KeyError:
                raise AttributeError(
                    "Attribute missing from tag: 'href' (line %d)." % link.sourceline)

            filename = os.path.join(self.path, href)
            if not os.path.exists(filename):
                raise ValueError(
                    "File not found: %s" % repr(href))

            rules = parse_xss(filename)

            for rule in rules:
                selector = lxml.cssselect.CSSSelector(rule.selector)
                for element in root.xpath(
                    selector.path, namespaces=rule.namespaces):
                    if rule.name:
                        element.attrib[
                            '{http://namespaces.repoze.org/xss}content'] = \
                            rule.name
                    if rule.structure:
                        element.attrib[
                            '{http://namespaces.repoze.org/xss}structure'] = \
                            rule.structure
                    if rule.attributes:
                        element.attrib[
                            '{http://namespaces.repoze.org/xss}attributes'] = \
                            rule.attributes
                        
            link.getparent().remove(link)
            
        return root, doctype
