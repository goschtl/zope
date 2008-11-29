import cgi
import os
import re
import glob
import lxml.cssselect

from copy import deepcopy

from zope import component

from chameleon.core import translation
from chameleon.core import config
from chameleon.core import etree
from chameleon.core import types
from chameleon.core import utils

from xss import parse_xss
from interfaces import IResourceLocation

true_values = 'true', '1', 'yes'

re_stylesheet_import = re.compile(
    r'^(\s*@import\surl*\()([^\)]+)(\);?\s*)$')

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

def rebase(context, request, rel_path, abs_path):
    return component.queryMultiAdapter(
        (context, request, abs_path), IResourceLocation) or rel_path

def ensure_absolute(path, relative_path):
    if not os.path.isabs(relative_path):
        return os.path.join(path, relative_path)
    return relative_path
    
class Element(translation.Element):
    """The XSS template language base element."""
    
    class node(translation.Node):
        define_symbol = '_define'
        composite_attr_symbol = '_composite_attr'
        rebase_symbol = '_rebase'

        ns_omit = (
            "http://xml.zope.org/namespaces/meta",
            "http://namespaces.repoze.org/xss")

        @property
        def omit(self):
            return self.element.xss_omit.lower() in true_values

        @property
        def dict_attributes(self):
            if self.element.xss_attributes is not None:
                xhtml_attributes = utils.get_attributes_from_namespace(
                    self.element, config.XHTML_NS)

                if self.element.prefix is None:
                    xhtml_attributes.update(utils.get_attributes_from_namespace(
                        self.element, None))

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
        def dynamic_attributes(self):
            path = self.element.getroottree().getroot().xss_path
            
            for scope in self.stream.scope:
                if 'context' in scope and 'request' in scope:
                    if self.element.xss_rebase is not None:
                        rel_url = self.element.attrib[self.element.xss_rebase]
                        abs_url = ensure_absolute(path, rel_url)
                        value = types.value("%s(context, request, %s, %s)" % (
                            self.rebase_symbol, repr(rel_url), repr(abs_url)))
                        value.symbol_mapping[self.rebase_symbol] = rebase
                        return [(types.declaration((self.element.xss_rebase,)), value)]
            
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
            if content is not None and self.define_slot is None:
                expression = types.value(
                    "%s or %s" % (self.define_symbol, repr(self.element.text)))

                if self.element.xss_structure.lower() not in true_values:
                    expression = types.escape((expression,))

                return expression

        @property
        def define_slot(self):
            name = self.element.xss_content
            if name is not None:
                variable = self.symbols.slot + utils.normalize_slot_name(name)
                for scope in self.stream.scope:
                    if variable in scope:
                        return name
        
        @property
        def static_attributes(self):
            xhtml_attributes = utils.get_attributes_from_namespace(
                self.element, config.XHTML_NS)

            if self.element.prefix is None:
                xhtml_attributes.update(utils.get_attributes_from_namespace(
                    self.element, None))

            return xhtml_attributes

        @property
        def skip(self):
            if self.define_slot is not None:
                return True
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

    xss_rebase = utils.attribute(
        '{http://namespaces.repoze.org/xss}rebase')

    xss_path = utils.attribute(
        '{http://namespaces.repoze.org/xss}path')                    

class MetaElement(translation.MetaElement):
    class node(translation.Node):
        rebase_symbol = '_rebase'

        @property
        def omit(self):
            if self.element.meta_omit is not None:
                return self.element.meta_omit or True
            if self.element.meta_replace:
                return True

        @property
        def content(self):
            path = self.element.getroottree().getroot().xss_path

            if self.element.xss_rebase and self.element.text:
                for scope in self.stream.scope:
                    if 'context' not in scope or 'request' not in scope:
                        continue
                    
                    m = re_stylesheet_import.match(self.element.text)
                    assert m is not None

                    before = m.group(1)
                    after = m.group(3)

                    rel_url = m.group(2)
                    abs_url = ensure_absolute(path, rel_url)

                    value = types.value(
                        "'<!-- %s' + %s(context, request, %s, %s) + '%s -->'" % (
                        before, self.rebase_symbol,
                        repr(rel_url), repr(abs_url), after))

                    value.symbol_mapping[self.rebase_symbol] = rebase
                    break
                else:
                    value = types.value("'<!-- %s -->'" % self.element.text)
                return value
            return self.element.meta_replace
        
    node = property(node)

    xss_rebase = utils.attribute(
        '{http://namespaces.repoze.org/xss}rebase')                    

    xss_path = utils.attribute(
        '{http://namespaces.repoze.org/xss}path')                    

class XSSTemplateParser(etree.Parser):
    """XSS template parser."""
    
    element_mapping = {
        config.XHTML_NS: {None: Element},
        config.META_NS: {None: MetaElement}}

class DynamicHTMLParser(XSSTemplateParser):
    slots = attributes = ()
    
    def __init__(self, filename):
        self.path = os.path.dirname(filename)

        # parse the body at initialization to fill the slots and
        # attributes lists
        self.file_dependencies = []
        self.parse(file(filename).read())

    def expand_tag(self, original, matches, attribute="href"):
        tag = original
        for nr, match in enumerate(matches):
            match = match[len(self.path)+1:]
            if nr == 0:
                tag.attrib[attribute] = match
            else:
                new = deepcopy(tag)
                new.attrib[attribute] = match
                tag.addnext(new)
                tag.tail = new.tail
                new.tail = "\n"
                tag = new
                
    def glob_resources(self, root, attribute, xpath, ns={}):
        """Resource globbing"""
        tags = root.xpath(xpath, namespaces=ns)
        for tag in tags:
            href = tag.attrib.get(attribute)
            matches = glob.glob(os.path.join(self.path, href))
            if len(matches):
                self.expand_tag(tag, matches, attribute)

    def parse(self, body):
        root, doctype = super(DynamicHTMLParser, self).parse(body)

        # set template path attribute on root element
        root.attrib[
            '{http://namespaces.repoze.org/xss}path'] = self.path
        
        # reset dynamic identifier lists
        self.slots = []
        self.attributes = []

        # process possible resource globbing
        self.glob_resources(root, "href", './/xmlns:link', ns={'xmlns': config.XHTML_NS})
        self.glob_resources(root, "src", './/xmlns:script', ns={'xmlns': config.XHTML_NS})

        # process dynamic rules
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

            # add to file dependencies
            self.file_dependencies.append(filename)
                        
            # parse and apply rules
            rules = parse_xss(filename)
            for rule in rules:
                selector = lxml.cssselect.CSSSelector(rule.selector)
                for element in root.xpath(
                    selector.path, namespaces=rule.namespaces):
                    if rule.name:
                        self.slots.append(rule.name)
                               
                        if rule.mode == 'content':
                            element.attrib[
                                '{http://namespaces.repoze.org/xss}content'] = \
                                rule.name
                        elif rule.mode == 'replace':
                            element.attrib[
                                '{http://namespaces.repoze.org/xss}content'] = \
                                rule.name
                            element.attrib[
                                '{http://namespaces.repoze.org/xss}omit'] = 'true'
                        elif rule.mode == 'append':
                            new = element.makeelement(
                                utils.xhtml_attr('div'))
                            new.attrib.update(
                                {'{http://namespaces.repoze.org/xss}content': rule.name,
                                 '{http://namespaces.repoze.org/xss}omit': 'true'})
                            element.append(new)
                            element = new
                        elif rule.mode == 'prepend':
                            new = element.makeelement(
                                utils.xhtml_attr('div'))
                            new.attrib.update(
                                {'{http://namespaces.repoze.org/xss}content': rule.name,
                                 '{http://namespaces.repoze.org/xss}omit': 'true'})
                            element.insert(0, new)
                            element = new
                        else:
                            raise ValueError(
                                "Unsupported insertion mode: %s" % rule.mode)
                            
                    if rule.structure:
                        element.attrib[
                            '{http://namespaces.repoze.org/xss}structure'] = \
                            rule.structure
                    if rule.attributes:
                        self.attributes.append(rule.attributes)
                        element.attrib[
                            '{http://namespaces.repoze.org/xss}attributes'] = \
                            rule.attributes
                        
            link.getparent().remove(link)

        # prepare reference rebase logic
        elements = root.xpath(
            './/xmlns:link[@href] | .//xmlns:img[@src] | .//xmlns:script[@src]',
            namespaces={'xmlns': config.XHTML_NS})
        for element in elements:
            href = element.attrib.get('href')
            if href is not None:
                element.attrib['{http://namespaces.repoze.org/xss}rebase'] = 'href'
            src = element.attrib.get('src')
            if src is not None:
                element.attrib['{http://namespaces.repoze.org/xss}rebase'] = 'src'
        elements = root.xpath(
            './/xmlns:style', namespaces={'xmlns': config.XHTML_NS})
        for element in elements:
            for comment in element:
                text = comment.text
                m = re_stylesheet_import.match(text)
                if m is not None:
                    index = element.index(comment)
                    element.remove(comment)
                    comment = element.makeelement(
                        utils.meta_attr('comment'))
                    element.insert(index, comment)
                    comment.attrib['{http://namespaces.repoze.org/xss}rebase'] = 'true'
                    comment.text = text

        return root, doctype
