##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""

$Id: view.py 39651 2005-10-26 18:36:17Z oestermeier $
"""
__docformat__ = 'restructuredtext'

import doctest, unittest
import cgi, urllib, os, time, sys, itertools

from string import Template
from persistent import Persistent

from zope.app import zapi
from zope.interface import implements
from zope.component import adapts
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces import IRequest
from zope.app.session.interfaces import ISession
from zope.security.proxy import removeSecurityProxy
from zope.security.checker import defineChecker, NoProxy

from zope.app.traversing.interfaces import TraversalError
from zope.app.traversing.interfaces import ITraversable
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import NotFound
from zope.app.publisher.browser import BrowserView


from zorg.ajax.interfaces import IAjaxPage
from zorg.ajax.interfaces import IAjaxLiveSearchPage
from zorg.ajax.interfaces import ILiveChanges
from zorg.ajax.interfaces import IAjaxUpdateable
from zorg.ajax.interfaces import IPageElement
from zorg.ajax.interfaces import ISettingsStorage


class AjaxPage(BrowserView) :
    """ A base class for ajax pages.
    
        Can be used to generate ajax calls:
        
        >>> request = TestRequest()
        >>> page = AjaxPage(None, request)
        
        The common usage is to provide a callback method that
        returns HTML fragments that can be used to substitute
        parts of the DOM tree of the calling browser page.
        
        >>> page.updater("element-id", "updateElement") #doctest: +ELLIPSIS
        "new Ajax.Updater('element-id', './@@updateElement', ..."
    """
    
    implements(IAjaxPage)
    
    _updater = Template(
                "new Ajax.Updater('$id', './@@$call', $args);")
                
    def __init__(self, context, request) :
        self.context = context
        self.request = request
        self.args = self.parseQuery()
    
    def parseQuery(self) :
        """ Parses the query string. """
        if 'QUERY_STRING' in self.request :
            return cgi.parse_qs(self.request['QUERY_STRING'])
        return {}
               
    def getSessionStorage(self) :
        """ Returns a session storage. """
        
        session = ISession(self.request)['zorg.ajax']
        if session.get("storage") is None :
            session["storage"] = SettingsStorage()
        return session["storage"]


    def parameter(self, key, type=None, default=None, storage=None) :
        """ Extract parameter from request or storage. 
        
        >>> request = TestRequest()
        >>> view = AjaxPage(None, request)
        >>> view.parameter("query") is None
        True
        
        The parameter is either extracted from the query string
        or the form data:
        
        >>> view = AjaxPage(None, TestRequest(QUERY_STRING='query=xyz'))
        >>> view.parameter("query")
        u'xyz'
        
        If you expect something different from a string you must provide
        a converter / factory, otherwise the parameter is returned
        as a unicode string.
  
        Note that the value is persistent between calls if a 
        session data container is provided :
        
        >>> view = AjaxPage(None, TestRequest(form={'num': '42'}))
        >>> session = view.getSessionStorage()
        >>> view.parameter("num", int, storage=session)
        42
        
        >>> view = AjaxPage(None, TestRequest())
        >>> view.parameter("num", int, storage=session)
        42
        
        """
        
        value = None
        if key in self.request :
            value = self.request[key]
        elif key in self.args :
            value = self.args[key][0]
        if value is None :
            if storage is not None :
                return getattr(storage, key, default)
            return default
        if type is None :
            if isinstance(value, str) :
                value = unicode(value, encoding="utf-8")
        else :
            value = type(value)
        if storage is not None :
            if getattr(storage, key, default) != value :
                setattr(storage, key, value)
        return value

        
    def filename(self, key, default=None) :
        """ Extracts the base filename from a posted form.
            Removes the leading path of IE uploads.
            
            Note that this method returns a utf-8 string.
        
        """
        
        form = self.request.form
        filename = getattr(form.get(key), "filename", default)
        if '\\' in filename :               # grr, IE hack
            return filename.split('\\')[-1]
        return os.path.basename(filename)
        
        
    def updater(self, id, call, parameters=None, 
                                asynchronous=True,
                                onComplete=None,
                                onLoading=None,
                                returnFalse=True) :
        """ Generates the javascript code for a dynamic update of a part 
            of the DOM tree.
            
            >>> request = TestRequest()
            >>> page = AjaxPage(None, request)
            >>> page.updater("id", "update") #doctest: +ELLIPSIS
            "new Ajax.Updater('id', './@@update', ..."
            
            Provides shortcuts for the rather lengthy generated javascript
            expressions. An args dict, for instance, is translated into
            query parameters :
            
            >>> page.updater("id", "update", {"topic":1}) #doctest: +ELLIPSIS
            "new Ajax.Updater('id', './@@update', {parameters:'topic=1'...
            
            
            >>> js = "doSomething();"
            >>> page.updater("id", "update", onComplete=js) #doctest: +ELLIPSIS
            "new Ajax.Updater...onComplete:...doSomething()...
            
            
        """
        args = []
        if parameters is not None :
            args.append("parameters:'%s'" % urllib.urlencode(parameters))
        if asynchronous :
            args.append("asynchronous:true")
        if onComplete :
            args.append("onComplete:function(request) {%s}" % onComplete)
        if onLoading :
            args.append("onLoading:function(request) {%s}" % onLoading)
        args = "{" + ",".join(args) + "}"
        javascript = self._updater.substitute(id=id, call=call, args=args)
        if returnFalse :
            javascript += " return false;"
        return javascript

    
    def answer(self, result) :
        response = self.request.response
        response.setHeader("Content-Type", "text/plain")
        response.setHeader('Last-Modified', rfc1123_date(time.time()))
        response.setHeader('Content-Length', len(result))
        return result
  

class ComposedAjaxPage(AjaxPage) :
    """ An AjaxPage that is composed of parts. The class provides special
        methods to access and update these parts.
    
    
    """
    
    registered_parts = None
    
    def lookUp(self, part=None) :
        """ Returns the part of the page or a NotFound error.
            The part is specified by an id or dotted_name that leads 
            to the python object that corresponds to the 
            DOM element in the browser.
            
            >>> class Part(object) :
            ...     implements(IAjaxUpdateable)
            ...     def __init__(self, id) : self.id = id
            
            Let's build a structured page:
            
            >>> request = TestRequest()
            >>> page = ComposedAjaxPage(None, request)
            >>> page.header = Part(1)
            >>> page.header.title = Part(2)
            
            We can now access the part via the path :
            
            >>> page.lookUp('header.title').id
            2
        
        """
            
        if part is None :
            part = self.parameter("part")
        
        registered = self.registered_parts and self.registered_parts.get(part)
        if registered :
            return registered
           
            # no directly registered, interpret as dotted_name resp. path
        if "." in part :
            path = part.split(".")
        else :
            path = list(part)   
        node = self
        for name in path :
            node = getattr(node, name, None)
            if node is None :
               raise NotFound(self, name, self.request)
               
        return node        
               

    def registerPart(self, id, element) :
        """ Registers a part under a given id. Can be used
            to make renderable subobjects directly accessible
            for the page. The id must be unique within the page.
            
            This can be used if an AjaxPage is combined with third party
            python objects. The only thing that must be ensured is
            that there is a IAjaxUpdateable adapter that ensures that the
            object can be rendered.
            
        """
        
        if self.registered_parts is None :
            self.registered_parts = {}    
        self.registered_parts[id] = element

           
    def renderPart(self, part=None, method=None, parameter=None) :
        """ Renders a part of the page.
        
            >>> class Part(object) :
            ...     implements(IAjaxUpdateable)
            ...     def __init__(self, content) : self.content = content
            ...     def render(self, method, parameter) : return self.content
            
            Let's build a structured page:
            
            >>> request = TestRequest()
            >>> page = ComposedAjaxPage(None, request)
            >>> page.header = Part('<h1>A header</h1>')
            >>> page.header.title = Part('<p>A title</p>')
            
            We can now access the part via the path :
            
            >>> page.renderPart('header.title')
            '<p>A title</p>'
            
            
            If path is not provided renderPart tries to extract it from the
            request. Note that the path is encoded as a dotted name :
            
            >>> page.request = TestRequest(form=dict(part='header.title'))
            >>> page.renderPart()
            '<p>A title</p>'

        """
        
        node = self.lookUp(part)
        renderer = IAjaxUpdateable(node, None)
            
        if renderer is not None :
            return renderer.render(method, parameter)
            
        if callable(node) :
            return node()
        return self.answer(str(node))

        
    def innerPart(self, part=None, method=None, parameter=None) :
        """ Returns the innerHTML that can be used to update a part of
            the DOM tree.
            
            >>> class Part(object) :
            ...     implements(IAjaxUpdateable)
            ...     def __init__(self, content) : self.content = content
            ...     def render(self, method, parameter) :
            ...         if method : getattr(self, method)(parameter)
            ...         return self.content
            ...     def onClick(self, arg) : self.content = '<p>clicked</p>'
            
            Let's build a structured page:
            
            >>> request = TestRequest()
            >>> page = ComposedAjaxPage(None, request)
            >>> page.header = Part('<p>A <b>structured</b> paragraph.</p>')
            
            We access the part exactly as in renderPart :
            
            >>> page.innerPart(['header'])
            'A <b>structured</b> paragraph.'
            
            
            >>> page.innerPart(['header'], method='onClick')
            'clicked'
            
       
        """
     
        html = self.renderPart(part, method, parameter)
        start = html.find('>')+1
        end = html.rfind('<')
        return html[start:end]
        
        
    def updaterForPart(self, dotted_name, parameters=None, 
                                asynchronous=True,
                                onComplete=None,
                                onLoading=None,
                                returnFalse=True) :
        """ Returns the javascript that is necessary to update a part
            of the DOM tree.
            
        >>> request = TestRequest()
        >>> page = ComposedAjaxPage(None, request)
        >>> page.updaterForPart('x.y', dict(method='onClick'))  #doctest: +ELLIPSIS
        "...Updater('x.y'...innerPart...parameters:'part=x.y&method=onClick'...
            
        """
       
        args = dict(part=dotted_name)
        if parameters :
            args.update(parameters)  
        return self.updater(dotted_name, "innerPart", args, 
                                asynchronous=asynchronous,
                                onComplete=onComplete,
                                onLoading=onLoading,
                                returnFalse=returnFalse)
        
 

class PageProperty(object) :
    """ A property class that allows to access parts of a page via
        python's setter and getter mechanism.
        
        >>> class Navigation(PageElement) :
        ...     implements(IAjaxUpdateable)
        ...     def render(self) : 
        ...         return '<div id="%s">Navigation</div>' % self.name
 
        >>> class AjaxPageWithNavigation(ComposedAjaxPage) :
        ...     navigation = PageProperty(key="navigation",
        ...                                        factory=Navigation)

        The property can be used for lazy access, i.e. the part is created
        on demand when the getter is called for the first time. The new object
        is saved for later access :
        
        >>> request = TestRequest()
        >>> page = AjaxPageWithNavigation(None, request)
        >>> access1 = page.navigation                  #doctest: +ELLIPSIS
        >>> access2 = page.navigation
        >>> access1 == access2
        True
        
        We can force a rebuild by deleting the property :
        
        >>> del page.navigation
        >>> access3 = page.navigation
        >>> access3 == access1
        False
        
        But we can of course also instantiate the part in advance :
        
        >>> page = AjaxPageWithNavigation(None, request)
        >>> part = Navigation(page)
        >>> page.navigation = part
        >>> page.navigation == part
        True
        
    """
    
    def __init__(self, key, factory) :
        self.key = key
        self.factory = factory
        
    def __set__(self, obj, value) :
        obj.__dict__[self.key] = value
        if IPageElement.providedBy(value) :
            value.name = self.key
        
    def __get__(self, obj, klass=None) :
        try :
            return obj.__dict__[self.key]
        except KeyError :
            value = self.factory(obj)
            self.__set__(obj,  value)  # save for later access
            return value
    
    def __delete__(self, obj) :
        del obj.__dict__[self.key]
        

class PageElement(object) :
    """ Represents a part of an AjaxPage. 
    
    >>> class Navigation(PageElement) :
    ...     implements(IAjaxUpdateable)
    ...     def render(self) : 
    ...         return '<div id="%s">Navigation</div>' % self.name

    >>> class AjaxPageWithNavigation(AjaxPage) :
    ...     navigation = PageProperty(key="navigation",
    ...                                        factory=Navigation)
    
    >>> context = object()
    >>> request = TestRequest()
    >>> page = AjaxPageWithNavigation(context, request)
    
    Since the element is defined via a page property, it is created on demand:
    
    >>> part = page.navigation             
    >>> part                            #doctest: +ELLIPSIS
    <...Navigation object at ...>

    Attribute lookup is performed along the parent relationship, i.e. a 
    child tries to find an attribute by asking its parent
    as long as the attribute is not defined in the child itself:
    
    >>> part.request == request
    True
    
    """
    
    implements(IPageElement)
    
    name = None
    
    def __init__(self, parent) :
        self.parent = parent
        
    def __getattr__(self, key) :
        return getattr(self.parent, key)
        

  
     
class SearchableAjaxPage(AjaxPage) :
    """ Mixin class for a live search, i.e. the search starts
        already while the user types the search keywords.
        
    """
    
    implements(IAjaxLiveSearchPage)
    
    def query(self) :
        return self.request.get('query')
   
    def liveSearch(self) :
        q = self.query()
        result = ['<div id="search-results">']
        if q :
            catalog = zapi.queryUtility(ICatalog, "liveSearch", context=self.context)
            criteria = {}
            criteria['text'] = q
            try :
                found = catalog.searchResults(**criteria)
                if found is not None :
                    for item in found :
                        url = zapi.absoluteURL(item, self.request)
                        title = IZopeDublinCore(item).title
                        result.append('<a href="%s">%s</a><br>' % (url, title))
            except parsetree.ParseError :
                pass
               
        result.append( '</div>')
        return self.answer("".join(result))



class SettingsStorage(Persistent) :
    """ A persistent object for user specific settings. Can be stored
        in the session or principal annotations.
    """

    implements(ISettingsStorage)


def test_suite():

    from zorg.ajax.tests import ajaxSetUp, ajaxTearDown
    
    return unittest.TestSuite((
        doctest.DocTestSuite(setUp=ajaxSetUp, tearDown=ajaxTearDown),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
        

