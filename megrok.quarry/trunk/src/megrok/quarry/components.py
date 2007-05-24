from zope import interface, component
from zope.publisher.browser import BrowserPage
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.viewlet.manager import ViewletManagerBase
from zope.viewlet.viewlet import ViewletBase
from zope.publisher.interfaces.browser import IBrowserView
from zope.publisher.publish import mapply
from grok import util, interfaces, formlib
import grok

class Layer(IDefaultBrowserLayer):
    pass


class Skin(object):
    pass


class ViewBase(object):

    def _render_template(self):
        namespace = self.template.pt_getContext()
        namespace['request'] = self.request
        namespace['view'] = self
        namespace['context'] = self.context
        namespace['static'] = self.static
        return self.template.pt_render(namespace)

    def application(self):
        obj = self.context
        while obj is not None:
            if isinstance(obj, grok.Application):
                return obj
            obj = obj.__parent__
        raise ValueErrror("No application found.")

    def site(self):
        obj = self.context
        while obj is not None:
            if isinstance(obj, grok.Site):
                return obj
            obj = obj.__parent__
        raise ValueErrror("No site found.")

    def application_url(self):
        obj = self.context
        while obj is not None:
            if isinstance(obj, grok.Application):
                return self.url(obj)
            obj = obj.__parent__
        raise ValueErrror("No application found.")

    def url(self, obj=None, name=None):
        # if the first argument is a string, that's the name. There should
        # be no second argument
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
        return util.url(self.request, obj, name)
        
    def redirect(self, url):
        return self.request.response.redirect(url)
        
    @property
    def response(self):
        return self.request.response

    


class View(BrowserPage, ViewBase):
    interface.implements(interfaces.IGrokView)

    def __init__(self, context, request):
        super(View, self).__init__(context, request)
        self.static = component.queryAdapter(
            self.request,
            interface.Interface,
            name=self.module_info.package_dotted_name
            )
        # static files for closest application
        self.app_static = component.queryAdapter(
            self.request,
            interface.Interface,
            name=self.application().__name__)
        # static files for closest site
        self.site_static = component.queryAdapter(
            self.request,
            interface.Interface,
            name=self.site().__name__)



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
    
    def update(self):
        pass

    
    def __getitem__(self, key):
        # XXX give nice error message if template is None
        return self.template.macros[key]

    

class ViewletManager(ViewletManagerBase, ViewBase):
    """  A grok.View-like ViewletManager
    """
    
    template = None

    def __init__(self, context, request, view):
        super(ViewletManager, self).__init__(context, request, view)
        self.static = component.queryAdapter(
            self.request,
            interface.Interface,
            name=self.module_info.package_dotted_name
            )

    def update(self):
        super(ViewletManager, self).update()


    def render(self):
        """See zope.contentprovider.interfaces.IContentProvider"""
        # Now render the view
        if self.template:
            #return self.template(viewlets=self.viewlets)
            return self._render_template()
        else:
            return u'\n'.join([viewlet.render() for viewlet in self.viewlets])

    def sort(self, viewlets):
        # sort by viewlet class name as default
        return sorted(viewlets, lambda x,y: cmp(x[0], y[0]))



class Viewlet(ViewletBase, ViewBase):
    """ A grok.View-like viewlet
    """


    def __init__(self, context, request, view, manager):
        super(Viewlet, self).__init__(context, request, view, manager)
        self.static = component.queryAdapter(
            self.request,
            interface.Interface,
            name=self.module_info.package_dotted_name
            )

    def update(self):
        pass

    def render(self):
        mapply(self.update, (), self.request)
        if self.request.response.getStatus() in (302, 303):
            # A redirect was triggered somewhere in update().  Don't
            # continue rendering the template or doing anything else.
            return

        template = getattr(self, 'template', None)
        if template is not None:
            return self._render_template()



class ContentProvider(ViewBase):

    def __init__(self, context, request, view):
        self.__parent__ = view
        self.context = context
        self.request = request
        self.static = component.queryAdapter(
            self.request,
            interface.Interface,
            name=self.module_info.package_dotted_name
            )        
        return self.request.response

    def update(self):
        pass

    def render(self):
        mapply(self.update, (), self.request)
        if self.request.response.getStatus() in (302, 303):
            # A redirect was triggered somewhere in update().  Don't
            # continue rendering the template or doing anything else.
            return

        template = getattr(self, 'template', None)
        if template is not None:
            return self._render_template()


        
