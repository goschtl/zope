import os
import translation
import codegen
import sys

class PageTemplate(object):
    registry = {}

    def __init__(self, body):
        self.body = body
        self.signature = hash(body)
        
    def cook(self, params):
        source, _globals = translation.translate(self.body, params)
        suite = codegen.Suite(source)

        self.source = source
        
        _globals.update(suite._globals)
        _locals = {}

        exec suite.code in _globals, _locals
        
        return _locals['render']

    def render(self, **kwargs):
        signature = self.signature + hash(",".join(kwargs.keys()))

        template = self.registry.get(signature)
        if not template:
            self.registry[signature] = template = self.cook(kwargs.keys())

        return template(**kwargs)
            
    def __call__(self, **kwargs):
        return self.render(**kwargs)

class PageTemplateFile(PageTemplate):
    def __init__(self, filename):
        self.filename = filename
        
    def _get_filename(self):
        return getattr(self, '_filename', None)

    def _set_filename(self, filename):
        self._filename = filename
        self._v_last_read = False

    filename = property(_get_filename, _set_filename)

    def render(self, **kwargs):
        if self._cook_check():
            self.body = open(self.filename, 'r').read()
            self.signature = hash(self.body)
            self._v_last_read = self.mtime()

        return PageTemplate.render(self, **kwargs)
            
    def _cook_check(self):
        if self._v_last_read and not __debug__:
            return

        if self.mtime() == self._v_last_read:
            return

        return True

    def mtime(self):
        try:
            return os.path.getmtime(self.filename)
        except OSError:
            return 0

class ViewPageTemplate(property):
    def __init__(self, body):
        self.template = PageTemplate(body)
        property.__init__(self, self.render)

    def render(self, view):
        def template(**kwargs):
            return self.template.render(view=view,
                                        context=view.context,
                                        request=view.request,
                                        options=kwargs)
        return template
    
class ViewPageTemplateFile(ViewPageTemplate):
    def __init__(self, filename):
        if not os.path.isabs(filename):
            package_name = sys._getframe(1).f_globals['__name__']
            path = sys.modules[package_name].__path__[0]
            filename = path + os.sep + filename

        # make sure file exists
        os.lstat(filename)
            
        self.template = PageTemplateFile(filename)
        property.__init__(self, self.render)
