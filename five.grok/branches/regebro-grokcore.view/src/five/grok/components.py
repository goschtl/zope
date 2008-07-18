import sys, os
import warnings

import martian
from zope import interface
from zope import component
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.app.pagetemplate.engine import TrustedAppPT
from zope.pagetemplate import pagetemplate, pagetemplatefile

from zope.publisher.publish import mapply

import Acquisition
from OFS.SimpleItem import SimpleItem
from five.grok import interfaces

from zope.app.container.contained import Contained
import persistent

from zope.publisher.browser import BrowserPage

class Model(SimpleItem):
    # XXX Inheritance order is important here. If we reverse this,
    # then containers can't be models anymore because no unambigous MRO
    # can be established.
    interface.implements(IAttributeAnnotatable, interfaces.IContext)

from grokcore.view.components import ViewMixin
class View(ViewMixin, BrowserPage, Acquisition.Implicit):
    pass    
    
class BaseTemplate(object):
    """Any sort of page template"""

    interface.implements(interfaces.ITemplate)

    __grok_name__ = ''
    __grok_location__ = ''

    def __repr__(self):
        return '<%s template in %s>' % (self.__grok_name__,
                                        self.__grok_location__)

    def _annotateGrokInfo(self, name, location):
        self.__grok_name__ = name
        self.__grok_location__ = location

    def _initFactory(self, factory):
        pass

class GrokTemplate(BaseTemplate):
    """A slightly more advanced page template

    This provides most of what a page template needs and is a good base for
    writing your own page template"""

    def __init__(self, string=None, filename=None, _prefix=None):

        # __grok_module__ is needed to make defined_locally() return True for
        # inline templates
        # XXX unfortunately using caller_module means that care must be taken
        # when GrokTemplate is subclassed. You can not do a super().__init__
        # for example.
        self.__grok_module__ = martian.util.caller_module()

        if not (string is None) ^ (filename is None):
            raise AssertionError(
                "You must pass in template or filename, but not both.")

        if string:
            self.setFromString(string)
        else:
            if _prefix is None:
                module = sys.modules[self.__grok_module__]
                _prefix = os.path.dirname(module.__file__)
            self.setFromFilename(filename, _prefix)

    def __repr__(self):
        return '<%s template in %s>' % (self.__grok_name__,
                                        self.__grok_location__)

    def _annotateGrokInfo(self, name, location):
        self.__grok_name__ = name
        self.__grok_location__ = location

    def _initFactory(self, factory):
        pass

    def namespace(self, view):
        # By default use the namespaces that are defined as the
        # default by the view implementation.
        return view.default_namespace()

    def getNamespace(self, view):
        namespace = self.namespace(view)
        namespace.update(view.namespace())
        return namespace
    
class TrustedPageTemplate(TrustedAppPT, pagetemplate.PageTemplate):
    pass

class TrustedFilePageTemplate(TrustedAppPT, pagetemplatefile.PageTemplateFile):
    pass

class PageTemplate(GrokTemplate):

    def setFromString(self, string):
        zpt = TrustedPageTemplate()
        if martian.util.not_unicode_or_ascii(string):
            raise ValueError("Invalid page template. Page templates must be "
                             "unicode or ASCII.")
        zpt.write(string)
        self._template = zpt

    def setFromFilename(self, filename, _prefix=None):
        self._template = TrustedFilePageTemplate(filename, _prefix)

    def _initFactory(self, factory):
        factory.macros = self._template.macros

    def render(self, view):
        namespace = self.getNamespace(view)
        template = self._template
        namespace.update(template.pt_getContext())
        return template.pt_render(namespace)
    
class IGrokLayer(interface.Interface):
    pass

class Skin(object):
    pass
