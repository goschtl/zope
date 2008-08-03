from zope import interface
from zope.annotation.interfaces import IAttributeAnnotatable

import grokcore.view

from grokcore.view.components import PageTemplate
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from grokcore.component.interfaces import IContext

import Acquisition
from OFS.SimpleItem import SimpleItem

class Model(SimpleItem):
    # XXX Inheritance order is important here. If we reverse this,
    # then containers can't be models anymore because no unambigous MRO
    # can be established.
    interface.implements(IAttributeAnnotatable, IContext)

class View(grokcore.view.View, Acquisition.Explicit):
    pass

class ZopeTwoPageTemplate(PageTemplate):

    def setFromString(self, string):
        raise NotImplemented

    def setFromFilename(self, filename, _prefix=None):
        self._template = ViewPageTemplateFile(filename, _prefix)
    
    def render(self, view):
        namespace = self.getNamespace(view)
        template = self._template.__of__(view)
        namespace.update(template.pt_getContext())
        return template(namespace)
