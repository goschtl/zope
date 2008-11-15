import os
import sys
import etree
import utils
import config
import doctypes
import filecache
import translation

class Template(object):
    """Constructs a template object using the template language
    defined by ``parser`` (``ZopePageTemplateParser`` or
    ``GenshiParser`` as of this writing). Must be passed an input
    string as ``body``. The ``format`` parameter supports values 'xml'
    and 'text'. Pass a value for ``encoding`` if you need to allow
    strings that are not unicode or plain ASCII."""

    compilers = {
        'xml': translation.Compiler,
        'text': translation.Compiler.from_text}

    format = 'xml'
    filename = '<string>'
    
    implicit_doctype = doctypes.xhtml
    explicit_doctype = None
    
    def __init__(self, body, parser, format=None, doctype=None, encoding=None):
        self.body = body
        self.parser = parser        
        self.signature = hash(body)
        self.registry = {}
        self.encoding = encoding
        
        if format is not None:
            self.format = format

        if doctype is not None:            
            self.explicit_doctype = doctype
        
    def __repr__(self):
        return u"<%s %s>" % (self.__class__.__name__, self.filename)

    def __call__(self, **kwargs):
        return self.render(**kwargs)
    
    @property
    def macros(self):
        return Macros(self.render_macro)

    @property
    def compiler(self):
        return self.compilers[self.format](
            self.body, self.parser,
            implicit_doctype=self.implicit_doctype,
            explicit_doctype=self.explicit_doctype,
            encoding=self.encoding)

    def cook(self, **kwargs):
        template = self.compiler(**kwargs)
        template.compile()
        return template
    
    def cook_check(self, parameters, **kwargs):
        key = tuple(parameters), \
              tuple(item for item in kwargs.iteritems()), \
              self.signature, self.explicit_doctype
        template = self.registry.get(key, None)
        if template is None:
            template = self.cook(parameters=parameters, **kwargs)
            self.registry[key] = template
        return template

    def render(self, **kwargs):
        template = self.cook_check(parameters=kwargs)
        return self.render_template(template, **kwargs)

    def render_macro(self, macro, global_scope=False, parameters={}):
        template = self.cook_check(
            parameters=parameters, macro=macro, global_scope=global_scope)
        return self.render_template(template, **parameters)
    
    def render_xinclude(self, **kwargs):
        return self.render_macro("", parameters=kwargs)

    def render_template(self, __template__, **kwargs):
        if config.DEBUG_MODE is False:
            return __template__.render(**kwargs)
        
        try:
            return __template__.render(**kwargs)
        except:
            utils.raise_template_exception(
                __template__.source, repr(self), kwargs, sys.exc_info())
                      
class TemplateFile(Template):
    """Constructs a template object using the template language
    defined by ``parser``. Must be passed an absolute (or
    current-working-directory-relative) filename as ``filename``. If
    ``auto_reload`` is true, each time the template is rendered, it
    will be recompiled if it has been changed since the last
    rendering."""
    
    global_registry = {}
    
    def __init__(self, filename, parser, format=None,  doctype=None,
                 auto_reload=config.DEBUG_MODE):
        Template.__init__(
            self, None, parser, format=format, doctype=doctype)

        self.auto_reload = auto_reload
        self.filename = filename = os.path.abspath(
            os.path.normpath(os.path.expanduser(filename)))

        # make sure file exists
        os.lstat(filename)

        # read template
        self.read()

        # persist template registry on disk
        
        if config.DISK_CACHE:
            self.registry = filecache.TemplateCache(filename)

        self.global_registry.setdefault(filename, self)
        self.xincludes = XIncludes(
            self.global_registry, os.path.dirname(filename), self.clone)
        
    def clone(self, filename, format=None):
        cls = type(self)
        return cls(
            filename, self.parser, format=format,
            doctype=self.explicit_doctype, auto_reload=self.auto_reload)
        
    def _get_filename(self):
        return getattr(self, '_filename', None)

    def _set_filename(self, filename):
        self._filename = filename
        self._v_last_read = False

    filename = property(_get_filename, _set_filename)

    def read(self):
        filename = self.filename
        mtime = self.mtime()
        fd = open(filename, 'r')
        self.body = body = fd.read()
        fd.close()
        self.signature = filename, mtime
        self._v_last_read = mtime

    def cook(self, **kwargs):
        try:
            template = self.compiler(**kwargs)
        except etree.XMLSyntaxError, exception:
            exception.msg += ' (%s)' % self.filename
            raise exception

        try:
            template.compile()
        finally:
            if config.DEBUG_MODE:
                filename = "%s.py" % self.filename
                f = open(filename, 'w')
                f.write(template.source)
                f.close()

        return template

    def cook_check(self, **kwargs):
        if self.auto_reload and self._v_last_read != self.mtime():
            self.read()

        return Template.cook_check(self, **kwargs)

    def render(self, **kwargs):
        kwargs[config.SYMBOLS.xincludes] = self.xincludes
        return super(TemplateFile, self).render(**kwargs)

    def mtime(self):
        try:
            return os.path.getmtime(self.filename)
        except (IOError, OSError):
            return 0

class XIncludes(object):
    """Dynamic XInclude registry providing a ``get``-method that will
    resolve a filename to a template instance. Format must be
    explicitly provided."""
    
    def __init__(self, registry, relpath, factory):
        self.registry = registry
        self.relpath = relpath
        self.factory = factory

    def get(self, filename, format):
        if not os.path.isabs(filename):
            filename = os.path.join(self.relpath, filename)        
        template = self.registry.get(filename)
        if template is not None:
            return template
        return self.factory(filename, format=format)
    
class Macro(object):
    def __init__(self, render):
        self.render = render

class Macros(object):
    def __init__(self, render_macro, **kwargs):
        self.render = render_macro
        self.bound_parameters = kwargs

    def __getitem__(self, name):
        def render(**kwargs):
            kwargs.update(self.bound_parameters)
            return self.render(name, parameters=kwargs)
        return Macro(render)

    def bind(self, **kwargs):
        return Macros(self.render, **kwargs)
