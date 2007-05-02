from zope import interface, component
from zope.publisher.browser import BrowserPage
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.publisher.publish import mapply
from grok import util, interfaces, formlib


class Layer(IDefaultBrowserLayer):
    pass


class Skin(object):
    pass


class View(BrowserPage):
    interface.implements(interfaces.IGrokView)

    def __init__(self, context, request):
        super(View, self).__init__(context, request)
        self.static = component.queryAdapter(
            self.request,
            interface.Interface,
            name=self.module_info.package_dotted_name
            )
        
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
    
    def _render_template(self):
        namespace = self.template.pt_getContext()
        namespace['request'] = self.request
        namespace['view'] = self
        namespace['context'] = self.context
        # XXX need to check whether we really want to put None here if missing
        namespace['static'] = self.static
        return self.template.pt_render(namespace)
    
    def __getitem__(self, key):
        # XXX give nice error message if template is None
        return self.template.macros[key]
    
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
        
    def update(self):
        pass
    

# class ViewletManager(ViewletManagerBase):
#     """  A grok.View-like ViewletManager
#     """
    
#     template = None

#     def __init__(self, context, request, view):
#         super(ViewletManager, self).__init__(context, request, view)
#         self.static = component.queryAdapter(
#             self.request,
#             interface.Interface,
#             name=self.module_info.package_dotted_name
#             )
        
#     def render(self):
#         """See zope.contentprovider.interfaces.IContentProvider"""
#         # Now render the view
#         if self.template:
#             #return self.template(viewlets=self.viewlets)
#             return self._render_template()
#         else:
#             return u'\n'.join([viewlet.render() for viewlet in self.viewlets])
                                                
#     @property
#     def response(self):
#         return self.request.response

#     def _render_template(self):
#         namespace = self.template.pt_getContext()
#         namespace['request'] = self.request
#         namespace['view'] = self
#         namespace['viewlets'] = self.viewlets
#         namespace['static'] = self.static
#         namespace['context'] = self.context
#         # XXX need to check whether we really want to put None here if missing
#         return self.template.pt_render(namespace)

#     def sort(self, viewlets):
#         # sort by viewlet class name as default
#         return sorted(viewlets, lambda x,y: cmp(x[0], y[0]))

#     def url(self, obj=None, name=None):
#         # if the first argument is a string, that's the name. There should
#         # be no second argument
#         if isinstance(obj, basestring):
#             if name is not None:
#                 raise TypeError(
#                     'url() takes either obj argument, obj, string arguments, '
#                     'or string argument')
#             name = obj
#             obj = None

#         if name is None and obj is None:
#             # create URL to view itself
#             obj = self
#         elif name is not None and obj is None:
#             # create URL to view on context
#             obj = self.context
#         return util.url(self.request, obj, name)

#     def redirect(self, url):
#         return self.request.response.redirect(url)


# class Viewlet(ViewletBase):
#     """ A grok.View-like viewlet
#     """


#     def __init__(self, context, request, view, manager):
#         super(Viewlet, self).__init__(context, request, view, manager)
#         self.static = component.queryAdapter(
#             self.request,
#             interface.Interface,
#             name=self.module_info.package_dotted_name
#             )


#     @property
#     def response(self):
#         return self.request.response


#     def render(self):
#         mapply(self.update, (), self.request)
#         if self.request.response.getStatus() in (302, 303):
#             # A redirect was triggered somewhere in update().  Don't
#             # continue rendering the template or doing anything else.
#             return

#         template = getattr(self, 'template', None)
#         if template is not None:
#             return self._render_template()

#     def _render_template(self):
#         namespace = self.template.pt_getContext()
#         namespace['request'] = self.request
#         namespace['view'] = self
#         namespace['context'] = self.context
#         # XXX need to check whether we really want to put None here if missing
#         namespace['static'] = self.static
#         return self.template.pt_render(namespace)

#     def __getitem__(self, key):
#         # XXX give nice error message if template is None
#         return self.template.macros[key]

#     def url(self, obj=None, name=None):
#         # if the first argument is a string, that's the name. There should
#         # be no second argument
#         if isinstance(obj, basestring):
#             if name is not None:
#                 raise TypeError(
#                     'url() takes either obj argument, obj, string arguments, '
#                     'or string argument')
#             name = obj
#             obj = None

#         if name is None and obj is None:
#             # create URL to view itself
#             obj = self
#         elif name is not None and obj is None:
#             # create URL to view on context
#             obj = self.context
#         return util.url(self.request, obj, name)

#     def redirect(self, url):
#         return self.request.response.redirect(url)

#     def update(self):
#         pass


