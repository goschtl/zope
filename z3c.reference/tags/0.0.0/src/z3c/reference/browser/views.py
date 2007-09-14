from zope.traversing.browser.absoluteurl import absoluteURL,AbsoluteURL
import urllib
from zope.traversing.browser.interfaces import IAbsoluteURL
from zope import component
from zope.traversing.interfaces import IContainmentRoot
noImage = '/@@/z3c.reference.resources/noimage.jpg'

class ViewReferenceAbsoluteURL(AbsoluteURL):

    """adapts a view reference to IAbsoluteURL

    >>> from z3c.reference.reference import ViewReference
    >>> from zope.publisher.browser import TestRequest
    >>> ref = ViewReference(view=u'http://www.zope.org/')
    >>> request = TestRequest()
    >>> view = ViewReferenceAbsoluteURL(ref,request)
    >>> view
    <z3c.reference.browser.views.ViewReferenceAbsoluteURL ...>
    >>> view()
    'http://www.zope.org/'

    >>> ref = ViewReference(target=site)
    >>> view = ViewReferenceAbsoluteURL(ref,request)
    >>> view()
    'http://127.0.0.1'

    >>> ref = ViewReference(target=site,view=u'index.html?x=1&y=2')
    >>> view = ViewReferenceAbsoluteURL(ref,request)
    >>> view()
    'http://127.0.0.1/index.html?x=1&y=2'
    
    """

    def __init__(self,context,request):
        self.context = context.target
        self.view = context.view
        self.request = request

    def __str__(self):
        if self.context is not None:
            if self.context.__name__ or IContainmentRoot.providedBy(
                self.context):
                view = component.getMultiAdapter((self.context, self.request),
                                                 IAbsoluteURL)
                try:
                    url = view()
                except TypeError:
                    return noImage
                if self.view is not None:
                    url = '%s/%s' % (url,self.view.encode('utf8'))
                return url
            else:
                # the target ist lost TODO:
                return noImage
        elif self.view is not None:
            return self.view.encode('utf8')
        
        raise TypeError("Can't get absolute url of reference,"
                        "because there is no target or view "
                        "specified.")
    __call__=__str__
    def breadcrumbs(self):
        if self.context is not None:
            view = component.getMultiAdapter((self.context, self.request),
                                             IAbsoluteURL)
            return view.breadcrumbs()
        raise TypeError("Can't get breadcrumbs of external reference")
        

