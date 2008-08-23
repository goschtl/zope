import martian

from zope.annotation.interfaces import IAttributeAnnotatable
from zope.app.pagetemplate.viewpagetemplatefile import ViewMapper
from zope import interface, component

from grokcore.component.interfaces import IContext
from grokcore.formlib.components import GrokForm as BaseGrokForm
from grokcore.formlib.components import default_display_template, default_form_template
from grokcore.view.components import PageTemplate
import grokcore.view

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser.pagetemplatefile import getEngine
from Products.Five.browser import resource
from Products.Five.formlib import formbase
from Products.PageTemplates.Expressions import SecureModuleImporter
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from OFS.SimpleItem import SimpleItem
import Acquisition


class Model(SimpleItem):
    # XXX Inheritance order is important here. If we reverse this,
    # then containers can't be models anymore because no unambigous MRO
    # can be established.
    interface.implements(IAttributeAnnotatable, IContext)


class View(grokcore.view.View, Acquisition.Explicit):
    pass


# TODO: This should probably move to Products.Five.browser

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
        here = Acquisition.aq_inner(self.context)

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

# forms from formlib

class GrokForm(BaseGrokForm):

    def __init__(self, *args):
        super(GrokForm, self).__init__(*args)
        self.__name__ = self.__view_name__
        # super should not work correctly since this is needed again.
        self.static = component.queryAdapter(
            self.request, interface.Interface,
            name = self.module_info.package_dotted_name)


class Form(GrokForm, formbase.PageForm, View):

    martian.baseclass()
    template = default_form_template

class AddForm(GrokForm, formbase.AddForm, View):

    martian.baseclass()
    template = default_form_template


class EditForm(GrokForm, formbase.EditForm, View):

    martian.baseclass()
    template = default_form_template


class DisplayForm(GrokForm, formbase.DisplayForm, View):

    martian.baseclass()
    template = default_display_template
