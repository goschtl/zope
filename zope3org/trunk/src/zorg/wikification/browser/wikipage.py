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

$Id: tests.py 38895 2005-10-07 15:09:36Z dominikhuber $
"""
__docformat__ = 'restructuredtext'

import re, urllib, cgi

import zope.event
from zope.app import zapi
from zope.interface import implements
from zope.app.traversing.interfaces import TraversalError
from zope.app.folder import Folder
from zope.app.file import File
from zope.app.file.interfaces import IFile
from zope.app.container.interfaces import IContainer
from zope.app.publisher.browser import BrowserView
from zope.app.traversing.interfaces import IPhysicallyLocatable
from zope.app.dublincore.interfaces import IZopeDublinCore
from zope.app.event.objectevent import ObjectCreatedEvent
from zope.app.event.objectevent import ObjectModifiedEvent
from zope.app.session.interfaces import ISession
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from zope.publisher.browser import TestRequest
from zope.i18n import MessageIDFactory

_ = MessageIDFactory("zorg.wikification")

from persistent import Persistent

from zorg.wikification.browser.interfaces import IWikiPage
from zorg.importer import IImporter
from zorg.kupusupport.adapters import html_body
from zorg.kupusupport.browser.views import KupuEditor
from zorg.kupusupport.interfaces import IKupuPolicy

from zorg.restsupport import rest2html
from zorg.restsupport import html2rest


    

class WikiPage(AbstractPage) :
    """ A wiki page that 'wikifies' a container with ordinary HTML documents.
    
        See wikification/README.txt for a definition of what 
        'wikification' means and doctests of the methods of this class.
    
        >>> from zorg.wikification.tests import buildSampleSite
        >>> site = buildSampleSite()
        >>> page = WikiPage(site, TestRequest())
         
    """
    
    implements(IWikiPage)

    supported = 'text/html', 'application/xhtml+xml', 'application/xml', 'text/xml'
    title = u"Wiki page"
    action = "/@@wiki.html"      # the action that wikifies
    add = "/@@kupuadd.html"
    verb = _('View')
    uris = {
            'home': '#',
            'login': '#',
            }
    untitled = u"Untitled"
   
    def __init__(self, context, request, container=None) :
        """ Initializes some usefull instance variables. 
        
        
        """
        super(WikiPage, self).__init__(context, request)
          
        self.macros = {}
        if container is None :
            self.container = self.getContainer() or context
        else :
            self.container = container
        
        site = self.site = IPhysicallyLocatable(self.container).getNearestSite()
        self.base = zapi.absoluteURL(site, request)   
        dc = IZopeDublinCore(self.context)
        self.dc = dc
        
        self.title = dc.title or self.untitled
        self.language = dc.Language()
        
    def isAbsoluteURL(self, link) :
        """ Returns true if the link is a complete URL. 
            
            Note that an absolute URL in this sense 
            might point to a local object.
        """
        
        for prefix in 'http:', 'ftp:', 'https:', 'mailto:' :
            if link.startswith(prefix) :
                return True
        return False
        
    def getContainer(self) :
        """ Returns the base container. Should be overwritten. """
        return None
                   
    def wikifyLink(self, link) :
        """
        Modifies dead relative links and leaves all other links untouched.
        
        Returns a tuple of a boolean indicating a modification and the 
        resulting link.
                
        >>> from zorg.wikification.tests import buildSampleSite
        >>> site = buildSampleSite()
        >>> request = TestRequest()
        >>> wiki = WikiPage(site, request)
        
        Anchors and absolute external links are left unmodified :
        
        >>> wiki.wikifyLink('#anchor')
        (False, '#anchor')
        >>> wiki.wikifyLink('http://www.zope.org')
        (False, 'http://www.zope.org')   
        
        Relative and internal absolute links are treated the same. If 
        a link can be traversed successfully only the specific wiki
        view is added to ensure that we remain in the wiki navigation :
       
        >>> wiki.wikifyLink('http://127.0.0.1/site')
        (False, 'http://127.0.0.1/site/@@wiki.html')
        >>> wiki.wikifyLink('http://127.0.0.1/site/folder/subfolder')
        (False, 'http://127.0.0.1/site/folder/subfolder/@@wiki.html')
        
        If the path cannot completely be resolved the link is changed to
        an add view call :
        
        >>> wiki.wikifyLink('http://127.0.0.1/site/folder/wikify.html')
        (True, 'http://127.0.0.1/site/folder/@@kupuadd.html?path=wikify.html')
        
        """

        site_url = zapi.absoluteURL(self.site, self.request)
        if link.startswith(site_url) :
            link = link[len(site_url)+1:]
            node = self.site
            url = site_url
        elif self.isAbsoluteURL(link) :
            return False, link
        elif link.startswith("#") :
            return False, link
        else :
            node = self.container
            url = zapi.absoluteURL(node, self.request)
        
        path = [x for x in link.split("/") if x]        
        while path :         
            try :
                name = path[0]
                node = zapi.traverseName(node, name)
                url += "/" + name
                name = path.pop(0)
            except TraversalError :
                break
        if path :
            appendix = urllib.urlencode({'path': "/".join(path)})
            return True, url + self.add + "?" + appendix
        
        return False, url + self.action
 
 
    def wikifyTextLink(self, text) :
        """ Modifies dead relative links and leaves
            all other links untouched.
        """
        
        name = text.replace(" ", "")
        try :
            zapi.traverseName(self.container, name)
            link = name
            label = text
        except TraversalError :
            appendix = urllib.urlencode({'path': name})
            link = self.base + self.add + "?" + appendix
            label = '[%s]' % text
        return '<a href="%s">%s</a>' % (link, label)
        
    def wikify(self, body) :
        """ 
            Renders HTML with dead relative links as 'wikified' HTML,
            i.e. dead relative links are converted to links that
            enable the user to add new pages.
        """
    
        from zorg.wikification.parser import BaseHTMLProcessor
        
        class LinkProcessor(BaseHTMLProcessor) :
            
            def __init__(self, caller) :
                BaseHTMLProcessor.__init__(self)
                self.caller = caller
                
            def unknown_starttag(self, tag, attrs):
                if tag == "a" :
                    modified = []
                    for key, value in attrs :
                        if key == "href" :
                            new, value = self.caller.wikifyLink(value)
                            if new :
                                modified.append(("class", "wiki-link"))
                        modified.append((key, value))
  
                    BaseHTMLProcessor.unknown_starttag(self, tag, modified)
                else :
                    BaseHTMLProcessor.unknown_starttag(self, tag, attrs)               
 
            def handle_data(self, text):
                # called for each block of plain text, i.e. outside of any tag and
                # not containing any character or entity references
                
                text_link = re.compile('\[.*?\]', re.VERBOSE)
                
                result = ""
                end = 0
                for m in text_link.finditer(text):
                    
                    start = m.start()
                    end = m.end()
                    result += text[end:start]
                    between = text[start+1:end-1]
                    result += self.caller.wikifyTextLink(between)
                    
                result += text[end:]
                self.pieces.append(result)
        
        
        processor = LinkProcessor(self)
        processor.feed(body)
        return processor.output()
     
      
    def nextURL(self) :
        url = zapi.absoluteURL(self.context, self.request)
        return url + self.action


class WikiContainerPage(WikiPage) :
    """ Wiki view for a container. """
    
    text = """<html><body>
              <p>No index.html found.<p>
              <p>Create a
                  <a href="index.html">new index page</a>?
              </p>
              </body></html>"""
    
    new = u"""<html><body>
              <p>Type something interesting here...<p>
              </body></html>"""
    
    empty = File(text, "text/html")
    
    untitled = u"Untitled Folder"
    
    
    def getContainer(self) :
        return self.context
        
    def getContent(self) :
        """ Returns the editable content of a container.
        
            Returns the content of index.html if available
            or a dummy message otherwise.
            
            >>> from zorg.wikification.tests import buildSampleSite
            >>> site = buildSampleSite()
            >>> print WikiContainerPage(site, TestRequest()).getContent()
            <html>
                <body>
                    <p>Wikifiable</p>
                    ...
                </body>
            </html>
            
        """
        file = self.context.get(u"index.html")
        if file is None :
            return self.new
        else :
            return unicode(file.data, encoding="utf-8")
        
    def getFile(self) :
        return self.context.get(u"index.html", self.empty)

    def renderBody(self) :
        """ Delegates the rendering to the WikiFilePage of the 
            index.html doocument.
            
        """
        
        file = self.getFile()
        return WikiFilePage(file, self.request, self.container).renderBody()

        
        
class WikiFilePage(WikiPage) :
    """ Wiki view for a file. """
    
    untitled = u"Untitled Document"
    
    def getContainer(self) :
        return self.context.__parent__
        
    def renderBody(self) :
        
        file = self.context

        if file.contentType in self.supported :
            body = html_body(file.data)
            return unicode(self.wikify(body), encoding="utf-8")
            
            #info = WikPageInfo(body, self.context, self.request, self.main)
       
        # file type not supported
        return "Sorry, not wikifiable at the moment."


class EditOptions(WikiPage) :
    """ An editor were the user can switch between Kupu, Rest and 
        other edit options. 
        
    """

    actions = dict(rest="./restedit.html", kupu="./kupuedit.html")
    
    _choose = ViewPageTemplateFile("./edit.pt")
            
    def __call__(self) :
        """ Redirect the user to the selected editor. """
        
        session = self.getSessionStorage()
        editor = self.parameter('editor', storage=session)
        if editor in self.actions :
            self.request.response.redirect(self.actions[editor])
            
        return self._choose()        


class WikiEditor(WikiPage) :   
    """ Base class for a wiki edit page. Provides methods that
        access and update file content.
        
        >>> from zorg.wikification.tests import buildSampleSite
        >>> site = buildSampleSite()
        >>> request = TestRequest("/", form=dict(rest="ReSt", editor="rest"))
        >>> editor = WikiEditor(site, request)
        >>> editor.getDataAndContentTypes()
        (u'ReSt', 'text/plain')
      
    """
    
    def __init__(self, context, request) :
        super(WikiEditor, self).__init__(context, request)  
        self.editor = self.parameter('editor', storage=self.session)
        
    def getDataAndContentTypes(self) :
        """ Extracts data and content type from request."""
        editor = self.editor
        request = self.request
        if editor == "rest" : # add named adapter or utility later
            data = self.parameter('rest')
            isType = "text/plain"
            asType = "text/plain"
        else :
            data = self.parameter('kupu')
            isType = "text/html"
            asType = "text/html"
        return data, isType, asType   
                
    def updateFile(self, file, content, contentType="text/html", asContentType=None):
        """Update the content object using the editor output.
        
           contentType describes the provided content
           targetContentType prescribes in which format the content should be
           saved.

        """
        if asContentType is None :
            asContentType = file.contentType
        else :
            file.contentType = asContentType
            
        assert asContentType in "text/html", "text/plain"
        
        if asContentType == "text/html" :
            data = rest2html(content)
        elif asContentType == "text/plain" :
            data = content
            
        file.data = data
        zope.event.notify(ObjectModifiedEvent(file))    
            
    def displayFile(self, file, asContentType=None):
        """Display the specific editor content as text/html
           or rest text/plain
        """
        
        if asContentType is None :
            asContentType = file.contentType
         
        assert asContentType in "text/html", "text/plain"
        
        if asContentType == "text/html" :
        
            if file.contentType == "text/html" :
                return unicode(html_body(file.data), encoding="utf-8")
                
            if file.contentType == "text/plain" :
                return RestToHTML(file.data)
                
        elif asContentType == "text/plain" :
        
            if file.contentType == "text/html" :
                return HTMLToRest(html_body(file.data))
            if file.contentType == "text/plain" :
                return file.data   
        
        
      
class EditWikiPage(WikiEditor, WikiFilePage) :
 
    verb = _('Edit')
    
    def display(self) :
        """ Returns the data that should be edited. """
        return self.displayFile(self.context)
    
    def update(self, editor=None):
        """ Saves the edited content and redirects to the wiki view. """
        
        data, isType, asType = self.getDataAndContentTypes()
        self.updateFile(self, context, data, isType, asType)
        self.request.response.redirect("wiki.html")
        

class CreateWikiPage(WikiEditor, WikiContainerPage) :

    verb = _('Add')
 
    def importURL(self, url) :
        """ Imports pages from an URL. """
        
        if url == "test" :
            from importer.tests import testURL
            url = testURL
        importer = IImporter(self.context)
        importer.verbosity = 1
        target = zapi.absoluteURL(self.context, self.request)
        importer.download(url, target)
        self.request.response.redirect(self.nextURL())

    def getContent(self) :
        return self.new
    
    def getAddPath(self) :
        """ Returns the path that is added to the container if the user
            creates a new wiki page.
        """
        filepath = self.request.form.get('path', 'index.html')
        return filepath.split(u'/')
        
    def createFile(self) :
        """
            Creates a file at the given path. Creates all intermediate
            folders if necessary.
            
        """        
        path = self.getAddPath()

        assert len(path) > 0
        
        container = base = self.container
        for name in path[:-1] :
            try :
                container = zapi.traverseName(base, name)
                assert IContainer.providedBy(base)
            except TraversalError :
                container = base[name] = Folder()
            base = container
         
        name = path[-1]
        if name in container :
            file = container[name]
        else :
            file = File()
            zope.event.notify(ObjectCreatedEvent(file))
            container[name] = file
            file = container[name] 
        return file

    def update(self, editor=None):
        """
            Generic store method.           
        """
        request = self.request
        data, isType, asType = self.getDataAndContentTypes()
        file = self.createFile()
        self.updateFile(file, data, isType, asType)        
        url = zapi.absoluteURL(file, self.request)
        request.response.redirect(url + self.action)

