#extjs widgets
import os.path, sys
from zope.viewlet.interfaces import IViewletManager
from zope.viewlet.viewlet import ViewletBase
from zope.viewlet.manager import WeightOrderedViewletManager
from zope.documenttemplate.untrusted import UntrustedHTML


def package_home(gdict):
    filename = gdict["__file__"]
    return os.path.dirname(filename)

class PythonTemplateFile(object):

    def __init__(self, filename, _prefix=None):
        path = self.get_path_from_prefix(_prefix)
        self.filename = os.path.join(path, filename)
        if not os.path.isfile(self.filename):
            raise ValueError("No such file", self.filename)

    def get_path_from_prefix(self, _prefix):
        if isinstance(_prefix, str):
            path = _prefix
        else:
            if _prefix is None:
                _prefix = sys._getframe(2).f_globals
            path = package_home(_prefix)
        return path

    def __call__(self, context, **kwargs):
        inFile = open(self.filename, 'rb')
        scope = {'r':'', 'context':context}
        scope.update(kwargs)
        exec inFile in scope
        return scope['r']


def escape(s):
    s = str(s).replace('\n','\\n').replace("'","\\'")
    return s


class IJSFormViewletManager(IViewletManager):
    """js form viewlet manager for rendering form generating javascript."""


class ExtJSFormViewletManager(WeightOrderedViewletManager):

    template = PythonTemplateFile('form-viewlet-manager.pyt')

    def render(self):
        return self.template(self)


class FormAwareViewlet(ViewletBase):

    def update(self):
        self.form = self.__parent__

    def hash(self, name):
        return str(hash(name)).replace('-','_')


class ExtJSFormViewlet(FormAwareViewlet):
    """Viewlet for js form declaration."""

    template = PythonTemplateFile('form-viewlet.pyt')

    def render(self):
        return self.template(self)


class ExtJSWidgetsViewlet(FormAwareViewlet):
    """Viewlet that hook in all the widgets."""

    template = PythonTemplateFile('form-widgets-viewlet.pyt')

    def render(self):
        return self.template(self, **globals())


class ExtJSButtonsViewlet(FormAwareViewlet):
    """Viewlet that add JS hooks for displaying buttons."""

    template = PythonTemplateFile('form-buttons-viewlet.pyt')

    def render(self):
        return self.template(self, **globals())
