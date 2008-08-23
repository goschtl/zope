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

# TODO: This should probably move to Products.Five.browser

from Acquisition import aq_inner
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from Products.PageTemplates.Expressions import SecureModuleImporter
from Products.Five.browser.pagetemplatefile import getEngine
from zope.app.pagetemplate.viewpagetemplatefile import ViewMapper

class ViewAwareZopePageTemplate(ZopePageTemplate):
    
    def pt_getEngine(self):
        return getEngine()
    
    def pt_getContext(self):
        try:
            root = self.getPhysicalRoot()
        except AttributeError:
            try:
                root = self.context.getPhysicalRoot()
            except AttributeError:
                root = None

        view = self._getContext()
        here = aq_inner(self.context)

        request = getattr(root, 'REQUEST', None)
        c = {'template': self,
             'here': here,
             'context': here,
             'container': here,
             'nothing': None,
             'options': {},
             'root': root,
             'request': request,
             'modules': SecureModuleImporter,
             }
        if view is not None:
            c['view'] = view
            c['views'] = ViewMapper(here, request)

        return c


class ZopeTwoPageTemplate(PageTemplate):

    def setFromString(self, string):
        self._template = ViewAwareZopePageTemplate(id=None, text=string)

    def setFromFilename(self, filename, _prefix=None):
        self._template = ViewPageTemplateFile(filename, _prefix)
    
    def render(self, view):
        namespace = self.getNamespace(view)
        template = self._template.__of__(view)
        namespace.update(template.pt_getContext())
        return template(namespace)

from Products.Five.browser import resource

class DirectoryResource(resource.DirectoryResource):
    # We subclass this, because we want to override the default factories for
    # the resources so that .pt and .html do not get created as page
    # templates

    resource_factories = {}
    for type, factory in (resource.DirectoryResource.resource_factories.items()):
        if factory is resource.PageTemplateResourceFactory:
            continue
        resource_factories[type] = factory


class DirectoryResourceFactory(resource.DirectoryResourceFactory):
    # __name__ is needed if you want to get url's of resources

    def __init__(self, name, path):
        self.__name = name
        self.__rsrc = self.factory(path, name)

    def __call__(self, request):
        resource = DirectoryResource(self.__rsrc, request)
        resource.__name__ = self.__name # We need to add name
        return resource
