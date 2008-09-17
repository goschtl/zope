import translation
import template
import generation
import doctypes
import etree
import config
import utils
import types

from StringIO import StringIO
from cPickle import dumps, loads

def pyexp(*exps):
    return types.parts([types.value(exp) for exp in exps])

def setup_stream(encoding=None):
    class symbols(translation.Node.symbols):
        out = '_out'
        write = '_write'

    out = StringIO()
    write = out.write
    stream = generation.CodeIO(symbols, encoding=encoding)
    return out, write, stream

def compile_xhtml(body, **kwargs):
    compiler = TestCompiler(
        body, mock_parser, implicit_doctype=doctypes.xhtml)
    return compiler(parameters=sorted(kwargs.keys()))

def render_xhtml(body, **kwargs):
    template = compile_xhtml(body, **kwargs)
    return template.render(**kwargs)    
    
def render_text(body, **kwargs):
    compiler = TestCompiler.from_text(
        body, mock_parser, implicit_doctype=doctypes.xhtml)
    template = compiler(parameters=sorted(kwargs.keys()))
    return template.render(**kwargs)    

def compile_template(parser, body, **kwargs):
    compiler = TestCompiler(
        body, parser, implicit_doctype=doctypes.xhtml)
    template = compiler(parameters=sorted(kwargs.keys()))
    return template.render(**kwargs)    

class TestCompiler(translation.Compiler):
    def __call__(self, *args, **kwargs):
        template = translation.Compiler.__call__(self, *args, **kwargs)
        template = loads(dumps(template))
        return template

class MockElement(translation.Element):
    class node(translation.Node):
        def __getattr__(self, name):
            return None

        @property
        def static_attributes(self):
            return utils.get_attributes_from_namespace(
                self.element, config.XHTML_NS)

        @property
        def omit(self):
            if self.element.meta_omit is not None:
                return self.element.meta_omit or True
            if self.content:
                return True
            if self.include:
                return True

        @property
        def content(self):
            return self.element.meta_replace
        
        @property
        def cdata(self):
            return self.element.meta_cdata

        @property
        def include(self):
            href = self.element.xi_href
            if href is not None:
                return types.value(repr(href))

        @property
        def format(self):
            return self.element.xi_parse

    node = property(node)

    xi_href = None
    xi_parse = None

class MockMetaElement(MockElement, translation.MetaElement):
    pass
    
class MockXiElement(MockElement):
    xi_href = utils.attribute('href')
    xi_parse = utils.attribute("parse", default="xml")

class MockParser(etree.Parser):
    element_mapping = {
        config.XHTML_NS: {None: MockElement},
        config.META_NS: {None: MockMetaElement},
        config.XI_NS: {None: MockXiElement}}

mock_parser = MockParser()

class MockTemplate(object):
    def __init__(self, body, parser=mock_parser, doctype=None):
        self.body = body
        self.parser = parser
        self.doctype = doctype
        
    @property
    def macros(self):
        def render(name, parameters={}):
            compiler = TestCompiler(self.body, self.parser)
            template = compiler(macro=name, parameters=parameters)
            return template.render(**parameters)
        return template.Macros(render)

    def render(self, **kwargs):
        compiler = TestCompiler(
            self.body, self.parser,
            implicit_doctype=doctypes.xhtml, explicit_doctype=self.doctype)
        template = compiler(parameters=sorted(kwargs.keys()))
        return template.render(**kwargs)    

    __call__ = render
