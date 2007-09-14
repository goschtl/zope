from zope.app.form.browser.widget import SimpleInputWidget
from zope.app.form.browser.textwidgets import TextWidget
from z3c.reference.reference import ViewReference,ImageReference
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.app.component import hooks
from zope import traversing
from zope.app.form.browser.widget import renderElement
from zc import resourcelibrary
from xml.dom.minidom import parse, parseString
from zope.traversing.interfaces import TraversalError        
import urlparse, cgi, urllib
from zope.cachedescriptors.property import Lazy


untitled = u'No Link defined'
undefined = u'Undefined'

emptyViewReference = ViewReference(view=u'#')
emptyImageReference = ImageReference(
    view=u'/@@/z3c.reference.resources/noimage.jpg')

def getText(nodelist):
    rc = ""
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc = rc + node.data
    return rc


def referenceFromURL(url,request,factory):

    site=hooks.getSite()
    siteURL = absoluteURL(site,request)
    if not url.startswith(siteURL):
        return ViewReference(view=url)
    url = url[len(siteURL)+1:]
    scheme,location,path,query,fragment = urlparse.urlsplit(url)
    tPath = map(lambda x: urllib.unquote(x.encode('utf-8')).decode('utf-8'),
        path.split('/'))
    # get the nearest traversable
    views = []
    while tPath:
        try:
            target = traversing.api.traverse(site,tPath)
            break
        except TraversalError:
            views.append(tPath.pop())

    query = query and u'?' + query or u''
    if views:
        views.reverse()
        views = u'/'.join(views)
        view = views + query
    else:
        view = query or None
    return factory(target=target,view=view)


class ViewReferenceWidget(TextWidget):

    """renders an "a" tag with the title and href attributes

    if no target

    >>> from zope.publisher.browser import TestRequest
    >>> from z3c.reference.schema import ViewReferenceField
    >>> from zope.app.folder import Folder
    >>> f = Folder()
    >>> site['folder'] = f
    >>> field = ViewReferenceField(title=(u'Title of Field'),
    ...     __name__='ref')
    >>> request = TestRequest()
    >>> w = ViewReferenceWidget(field,request)
    >>> w()
    u'<input class="hiddenType" id="field.ref" .../>...</a>'
    >>> request.form['field.ref']=u'http://127.0.0.1/folder'
    >>> res = w.getInputValue()
    >>> res
    <z3c.reference.reference.ViewReference object at ...>

    >>> res.view is None
    True
    
    >>> res.target is f
    True

    >>> request.form['field.ref']=u'http://127.0.0.1/folder/index.html'
    >>> res = w.getInputValue()
    >>> res.target is f
    True
    >>> res.view
    u'index.html'
    >>> absoluteURL(res,request)
    'http://127.0.0.1/folder/index.html'

    >>> request.form['field.ref']=u'http://127.0.0.1/folder/index.html?x=1&y=2'
    >>> res = w.getInputValue()
    >>> res.target is f
    True
    >>> res.view
    u'index.html?x=1&y=2'
    >>> absoluteURL(res,request)
    'http://127.0.0.1/folder/index.html?x=1&y=2'

    >>> print w()
    <input class="hiddenType" .../><a href="..." ...</a>

    >>> ff = Folder()
    >>> f[u'second'] = ff
    >>> request.form['field.ref']=u'http://127.0.0.1/folder/second/index.html?x=1&y=2'
    >>> res = w.getInputValue()
    >>> res.target is ff
    True

    
    """

    tag = u'input'
    type = u'hidden'
    cssClass = u''
    extra =  u'z3c:explorerLink="@@explorer.html?link=1"'
    refTag = u'a'
    refTagOnClick="z3cReferenceOnClick(this); return false;"
    _emptyReference = emptyViewReference


    def __init__(self, *args):
        resourcelibrary.need('z3c.reference')
        super(ViewReferenceWidget, self).__init__(*args)

        
    def __call__(self):
        resourcelibrary.need('z3c.reference')
        hidden = super(ViewReferenceWidget,self).__call__()
        if self._renderedValueSet():
            ref = self._data
        else:
            ref = self.context.default
        if not ref:
            try:
                ref = self.context.get(self.context.context)
            except:
                ref = None
        if ref is None:
            ref = self._emptyReference
        url = absoluteURL(ref,self.request)
        if ref.target is not None:
            contents = getattr(ref.target,'title',None) or \
                       ref.target.__name__
        else:
            contents = untitled
        tag = renderElement(self.refTag,
                            href=url,
                            name=self.name,
                            id=self.name + '.tag',
                            title=contents,
                            onclick=self.refTagOnClick,
                            contents=contents,
                            style=self.style,
                            extra=self.extra)
        return hidden + tag

    def _getFormValue(self):
        res = super(ViewReferenceWidget,self)._getFormValue()
        return res

    def _toFormValue(self, value):
        if value == self.context.missing_value:
            return self._missing
        try:
            url = absoluteURL(value,self.request)
        except TypeError:
            return self._missing
        return url
    
    def _toFieldValue(self, input):
        if input == self._missing:
            return self.context.missing_value
        return referenceFromURL(input,self.request,
                                self._emptyReference.__class__)
        


class ObjectReferenceWidget(ViewReferenceWidget):
    
    @Lazy
    def extra(self):
        iface = self.context.refSchema
        name = u'%s.%s' % (iface.__module__,iface.__name__)
        return u'z3c:explorerLink="@@explorer.html?link=1&schema=%s"' % \
               name


class ImageReferenceWidget(ViewReferenceWidget):

    """renders an "a" tag with the title and href attributes

    if no target

    >>> from zope.publisher.browser import TestRequest
    >>> from z3c.reference.schema import ImageReferenceField
    >>> from zope.app.folder import Folder
    >>> f = Folder()
    >>> site['folder'] = f
    >>> field = ImageReferenceField(title=(u'Title of Field'),
    ...     __name__='ref',size=(10,10))
    >>> request = TestRequest()
    >>> w = ImageReferenceWidget(field,request)
    >>> print w()
    <input .../><img ...height="10" id="field.ref.tag" .../>
    
    """


    
    refTag = u'img'
    _emptyReference = emptyImageReference
    extra = u''

    
    def __call__(self):
        hidden = super(ViewReferenceWidget,self).__call__()
        if self._renderedValueSet():
            ref = self._data
        else:
            ref = self.context.default
        if not ref:
            try:
                ref = self.context.get(self.context.context)
            except:
                ref = None
        if ref is None:            
            ref = self._emptyReference
            url = absoluteURL(ref, self.request)
        else:
            # return uid instead of absoluteURL cuz of umlaut problems
            url = str(absoluteURL(ref.target,self.request)) + '/' + ref.view
        if ref.target is not None:
            title = getattr(ref.target,'title',None) or \
                       ref.target.__name__
        else:
            title = untitled
        width,height = self.context.size
        kwords = dict(src=url,
                      name=self.name,
                      id=self.name + '.tag',
                      title=title,
                      alt=title,
                      width=width,
                      height=height,
                      onclick=self.refTagOnClick,
                      style=self.style,
                      extra=self.extra)
        tag = renderElement(self.refTag,**kwords)
        return hidden + tag


    def _toFormValue(self, value):
        if value == self.context.missing_value:
            return self._missing
        try:
            # return uid instead of absoluteURL cuz of umlaut problems
            url = str(absoluteURL(value.target,self.request)) + '/' + value.view
        except TypeError:
            return self._missing
        return url
