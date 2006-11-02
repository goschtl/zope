from zope.traversing.namespace import SimpleHandler
from zope import component,interface
from zope.publisher.browser import BrowserPage,BrowserView
from zope.app.form.interfaces import IInputWidget, IDisplayWidget
from interfaces import IAjaxWidget
from zope.traversing.browser.absoluteurl import absoluteURL
from zc import resourcelibrary
from zope.app.form.browser.textwidgets import renderElement
from zope.security.proxy import removeSecurityProxy
from interfaces import IAjaxFormTraverser,IAjaxWidgetTraverser

class Ajax(BrowserPage):
    #implements(IAbsoluteURL)

    def __call__(self):
        return u"no call"

    def publishTraverse(self, request, name):

        name = name.split('.')[-1]
        fields = removeSecurityProxy(self.context.form_fields) 
        form_field = fields[name]
        field = form_field.field
        interface = field.interface
        adapter = interface(removeSecurityProxy(self.context).context)
        field = field.bind(adapter)
        if form_field.custom_widget is not None:
            widget = form_field.custom_widget(field, request)
        else:
            widget = component.getMultiAdapter((field, request),
                                               IAjaxWidget)
        prefix = removeSecurityProxy(self.context).prefix
        if form_field.prefix:
            prefix += '.' + form_field.prefix
        widget.setPrefix(prefix)
        widget.__form__=self.context
        return widget


class AjaxWidgetTraverser(BrowserPage):

    interface.implements(IAjaxWidgetTraverser)

    def __call__(self):
        # renders a widget loader
        #form = component.getMultiAdapter((self.context, self.request),
        #                                 name=self.__parent__.__name__)
        url = absoluteURL(self.context,self.request)
        url = '%s/++ajax++%s/%s' % (url,self.__parent__.__name__,
                                    self.__name__)
        # we switch to display as standard mode
        html =  renderElement('span',
                              cssClass='ajax:container',
                              extra='ajax:src="%s/display"' % url,
                              contents='Loading ...')
        return html

    def publishTraverse(self, request, name):

        if name=='input':
            forInput = True
        elif name=='display':
            forInput = False
        else:
            return super(AjaxWidgetTraverser,self).publishTraverse(
                request,name)
        form = component.getMultiAdapter((self.context, self.request),
                                         name=self.__parent__.__name__)

        # hm, how can we prevent this line?
        fieldName = self.__name__.split('.')[-1]
        fields = form.form_fields
        #import pdb;pdb.set_trace()
        form_field = fields[fieldName]
        field = form_field.field
        interface = field.interface
        adapter = interface(form.context)
        field = field.bind(adapter)
        if form_field.custom_widget is not None:
            widget = form_field.custom_widget(field, request)
        else:
            widget = component.getMultiAdapter((field, request),
                                               IAjaxWidget)
        prefix = form.prefix
        if form_field.prefix:
            prefix += '.' + form_field.prefix
        widget.setPrefix(prefix)
        widget.__form__=form
        widget.__parent__=self
        if forInput:
            return widget.renderInput
        else:
            return widget.renderDisplay


from zope.traversing.adapters import DefaultTraversable
class AjaxWidgetTraversable(DefaultTraversable):

    def traverse(self, name, furtherPath):
        if not name in ('input','display'):
            return super(AjaxWidgetTraversable,self).traverse(
                name,furtherPath)
        
        return self._subject.publishTraverse(self._subject.request,
                                             name)
        

class AjaxFormTraversable(DefaultTraversable):

    def traverse(self, name, furtherPath):
        wt = AjaxWidgetTraverser(self._subject.context,
                                 self._subject.request)
        wt.__parent__=self._subject
        wt.__name__=name
        return wt
    

class AjaxFormTraverser(BrowserPage):

    interface.implements(IAjaxFormTraverser)

    def __init__(self,context,request,name):
        super(AjaxFormTraverser,self).__init__(context,request)
        self.__name__=name

    def __call__(self):
        # renders a form loader
        view = component.getMultiAdapter((self.context, self.request),
                                         name=self.__name__)
        url = absoluteURL(view,self.request)
        resourcelibrary.need('z3c_ajax')
        # remember: forms only have one display mode, so we load them
        # from their location
        html =  renderElement('div',
                              cssClass='ajax:container',
                              extra='ajax:src="%s"' % url,
                              contents='Loading ...')
        return html

    def publishTraverse(self, request, name):

        wt = AjaxWidgetTraverser(self.context,request)
        wt.__parent__=self
        wt.__name__=name
        return wt

class AjaxHandler(SimpleHandler):

    """returns the ajax view widget for a given field in a view"""

    def __init__(self,context,request=None):
        super(AjaxHandler,self).__init__(context,request)
        self.request=request

    def traverse(self,name,ignored):
        # context is a content object
        return AjaxFormTraverser(self.context,self.request,name)

