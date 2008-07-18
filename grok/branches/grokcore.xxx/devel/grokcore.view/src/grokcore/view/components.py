import os
import sys

from zope import component
from zope import interface
from zope.publisher.publish import mapply
from zope.security.permission import Permission
from zope.pagetemplate import pagetemplate, pagetemplatefile
from zope.app.pagetemplate.engine import TrustedAppPT
from zope.app.publisher.browser import directoryresource
from zope.app.publisher.browser.pagetemplateresource import \
    PageTemplateResourceFactory

import martian

from grokcore.view import util, interfaces


class Permission(Permission):
    pass


#XXX rename to GrokView
class ViewMixin(object):

    def __init__(self, context, request):
        super(ViewMixin, self).__init__(context, request)
        self.__name__ = self.__view_name__
        self.static = component.queryAdapter(
            self.request,
            interface.Interface,
            name=self.module_info.package_dotted_name
            )
        
    def _update_and_render(self):
        mapply(self.update, (), self.request)
        if self.request.response.getStatus() in (302, 303):
            # A redirect was triggered somewhere in update().  Don't
            # continue rendering the template or doing anything else.
            return

        template = getattr(self, 'template', None)
        if template is not None:
            return self._render_template()
        return mapply(self.render, (), self.request)

    def _render_template(self):
        return self.template.render(self)

    @property
    def response(self):
        return self.request.response

    def __call__(self):
        mapply(self.update, (), self.request)
        if self.request.response.getStatus() in (302, 303):
            # A redirect was triggered somewhere in update().  Don't
            # continue rendering the template or doing anything else.
            return

        template = getattr(self, 'template', None)
        if template is not None:
            return self._render_template()
        return mapply(self.render, (), self.request)
    
    def url(self, obj=None, name=None, data=None):
        """Return string for the URL based on the obj and name. The data
        argument is used to form a CGI query string.
        """
        if isinstance(obj, basestring):
            if name is not None:
                raise TypeError(
                    'url() takes either obj argument, obj, string arguments, '
                    'or string argument')
            name = obj
            obj = None

        if name is None and obj is None:
            # create URL to view itself
            obj = self
        elif name is not None and obj is None:
            # create URL to view on context
            obj = self.context

        if data is None:
            data = {}
        else:
            if not isinstance(data, dict):
                raise TypeError('url() data argument must be a dict.')

        return util.url(self.request, obj, name, data=data)

    def redirect(self, url):
        return self.request.response.redirect(url)

    def update(self):
        pass

    def namespace(self):
        return {}

    def default_namespace(self):
        namespace = {}
        namespace['context'] = self.context
        namespace['request'] = self.request
        namespace['static'] = self.static
        namespace['view'] = self
        return namespace
    
    def application_url(self, name=None):
        raise NotImplementedError


class GrokForm(object):
    """Mix-in to consolidate zope.formlib's forms with grok.View and to
    add some more useful methods.

    The consolidation needs to happen because zope.formlib's Forms have
    update/render methods which have different meanings than
    grok.View's update/render methods.  We deal with this issue by
    'renaming' zope.formlib's update() to update_form() and by
    disallowing subclasses to have custom render() methods."""

    def update(self):
        """Subclasses can override this method just like on regular
        grok.Views. It will be called before any form processing
        happens."""

    def update_form(self):
        """Update the form, i.e. process form input using widgets.

        On zope.formlib forms, this is what the update() method is.
        In grok views, the update() method has a different meaning.
        That's why this method is called update_form() in grok forms."""
        super(GrokForm, self).update()

    def render(self):
        """Render the form, either using the form template or whatever
        the actions returned in form_result."""
        # if the form has been updated, it will already have a result
        if self.form_result is None:
            if self.form_reset:
                # we reset, in case data has changed in a way that
                # causes the widgets to have different data
                self.resetForm()
                self.form_reset = False
            self.form_result = self._render_template()

        return self.form_result

    # Mark the render() method as a method from the base class. That
    # way we can detect whether somebody overrides render() in a
    # subclass (which we don't allow).
    render.base_method = True

    def __call__(self):
        mapply(self.update, (), self.request)
        if self.request.response.getStatus() in (302, 303):
            # A redirect was triggered somewhere in update().  Don't
            # continue rendering the template or doing anything else.
            return

        self.update_form()
        return self.render()


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


class PageTemplateFile(PageTemplate):
    # For BBB

    def __init__(self, filename, _prefix=None):
        self.__grok_module__ = martian.util.caller_module()
        if _prefix is None:
            module = sys.modules[self.__grok_module__]
            _prefix = os.path.dirname(module.__file__)
        self.setFromFilename(filename, _prefix)


class DirectoryResource(directoryresource.DirectoryResource):
    # We subclass this, because we want to override the default factories for
    # the resources so that .pt and .html do not get created as page
    # templates

    resource_factories = {}
    for type, factory in (directoryresource.DirectoryResource.
                          resource_factories.items()):
        if factory is PageTemplateResourceFactory:
            continue
        resource_factories[type] = factory


class DirectoryResourceFactory(object):
    # We need this to allow hooking up our own GrokDirectoryResource
    # and to set the checker to None (until we have our own checker)

    def __init__(self, path, name):
        # XXX we're not sure about the checker=None here
        self.__dir = directoryresource.Directory(path, None, name)
        self.__name = name

    def __call__(self, request):
        resource = DirectoryResource(self.__dir, request)
        resource.__name__ = self.__name
        return resource
