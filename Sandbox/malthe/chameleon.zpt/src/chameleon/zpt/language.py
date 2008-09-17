from zope import component

import itertools

from chameleon.core import translation
from chameleon.core import config
from chameleon.core import etree
from chameleon.core import utils

import interfaces
import expressions

class ZopePageTemplateElement(translation.Element):
    """Zope Page Template element.

    Implements the ZPT subset of the attribute template language.
    """

    class node(translation.Node):
        @property
        def omit(self):
            if self.element.tal_omit is not None:
                return self.element.tal_omit or True
            if self.element.meta_omit is not None:
                return self.element.meta_omit or True
            if self.element.tal_replace or self.element.meta_replace:
                return True
            if self.element.metal_use or self.element.metal_fillslot:
                return True
            
        @property
        def define(self):
            return self.element.tal_define

        @property
        def condition(self):
            return self.element.tal_condition

        @property
        def repeat(self):
            return self.element.tal_repeat

        @property
        def content(self):
            return self.element.tal_content or self.element.tal_replace or \
                   self.element.meta_replace

        @property
        def skip(self):
            if self.define_slot:
                variable = self.symbols.slot + self.define_slot
                if variable in itertools.chain(*self.stream.scope):
                    return True

            return self.content or \
                   self.use_macro or self.translate is not None

        @property
        def dynamic_attributes(self):
            return (self.element.tal_attributes or ()) + \
                   (self.element.meta_attributes or ())

        @property
        def translated_attributes(self):
            return self.element.i18n_attributes
        
        @property
        def static_attributes(self):
            return utils.get_attributes_from_namespace(
                self.element, config.XHTML_NS)
            
        @property
        def translate(self):
            return self.element.i18n_translate

        @property
        def translation_name(self):
            return self.element.i18n_name

        @property
        def translation_domain(self):
            return self.element.i18n_domain

        @property
        def use_macro(self):
            return self.element.metal_use
        
        @property
        def define_slot(self):
            return self.element.metal_defineslot

        @property
        def fill_slot(self):
            return self.element.metal_fillslot        

        @property
        def cdata(self):
            return self.element.meta_cdata

    node = property(node)

    @property
    def translator(self):
        while self.meta_translator is None:
            self = self.getparent()
            if self is None:
                raise ValueError("Default expression not set.")

        return component.getUtility(
            interfaces.IExpressionTranslator, name=self.meta_translator)

    metal_define = None
    metal_use = None
    metal_fillslot = None
    metal_defineslot = None

    i18n_domain = None
    i18n_translate = None
    i18n_attributes = None
    
    tal_define = None
    tal_condition = None
    tal_replace = None
    tal_content = None
    tal_repeat = None
    tal_attributes = None

    meta_translator = etree.Annotation(
        utils.meta_attr('translator'))

class XHTMLElement(ZopePageTemplateElement):
    """XHTML namespace element."""

    tal_define = utils.attribute(
        utils.tal_attr('define'), lambda p: p.definitions)
    tal_condition = utils.attribute(
        utils.tal_attr('condition'), lambda p: p.tales)
    tal_repeat = utils.attribute(
        utils.tal_attr('repeat'), lambda p: p.definition)
    tal_attributes = utils.attribute(
        utils.tal_attr('attributes'), lambda p: p.definitions)
    tal_content = utils.attribute(
        utils.tal_attr('content'), lambda p: p.output)
    tal_replace = utils.attribute(
        utils.tal_attr('replace'), lambda p: p.output)
    tal_omit = utils.attribute(
        utils.tal_attr('omit-tag'), lambda p: p.tales)
    tal_default_expression = utils.attribute(
        utils.tal_attr('default-expression'), encoding='ascii')
    metal_define = utils.attribute(
        utils.metal_attr('define-macro'))
    metal_use = utils.attribute(
        utils.metal_attr('use-macro'), lambda p: p.tales)
    metal_fillslot = utils.attribute(
        utils.metal_attr('fill-slot'))
    metal_defineslot = utils.attribute(
        utils.metal_attr('define-slot'))
    i18n_translate = utils.attribute(
        utils.i18n_attr('translate'))
    i18n_attributes = utils.attribute(
        utils.i18n_attr('attributes'), lambda p: p.mapping)
    i18n_domain = utils.attribute(
        utils.i18n_attr('domain'))
    i18n_name = utils.attribute(
        utils.i18n_attr('name'))
    
class MetaElement(XHTMLElement, translation.MetaElement):
    pass

class TALElement(ZopePageTemplateElement):
    """TAL namespace element."""
    
    tal_define = utils.attribute(
        ("define", utils.tal_attr("define")), lambda p: p.definitions)
    tal_condition = utils.attribute(
        ("condition", utils.tal_attr("condition")), lambda p: p.tales)
    tal_replace = utils.attribute(
        ("replace", utils.tal_attr("replace")), lambda p: p.output)
    tal_repeat = utils.attribute(
        ("repeat", utils.tal_attr("repeat")), lambda p: p.definition)
    tal_attributes = utils.attribute(
        ("attributes", utils.tal_attr("attributes")), lambda p: p.tales)
    tal_content = utils.attribute(
        ("content", utils.tal_attr("content")), lambda p: p.output)
    tal_omit = utils.attribute(
        ("omit-tag", utils.tal_attr("omit-tag")), lambda p: p.tales, u"")    
    
class METALElement(ZopePageTemplateElement):
    """METAL namespace element."""

    tal_omit = True
    
    metal_define = utils.attribute(
        ("define-macro", utils.metal_attr("define-macro")))
    metal_use = utils.attribute(
        ('use-macro', utils.metal_attr('use-macro')), lambda p: p.tales)
    metal_fillslot = utils.attribute(
        ('fill-slot', utils.metal_attr('fill-slot')))
    metal_defineslot = utils.attribute(
        ('define-slot', utils.metal_attr('define-slot')))

class Parser(etree.Parser):
    """Zope Page Template parser."""
    
    element_mapping = {
        config.XHTML_NS: {None: XHTMLElement},
        config.META_NS: {None: MetaElement},
        config.TAL_NS: {None: TALElement},
        config.METAL_NS: {None: METALElement}}

    default_expression = 'python'

    def __init__(self, default_expression=None):
        if default_expression is not None:
            self.default_expression = default_expression

    def parse(self, body):
        root, doctype = super(Parser, self).parse(body)
        root.meta_translator = self.default_expression
        return root, doctype
