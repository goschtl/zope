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

from zope.app import zapi
from zope.interface import implements
from zope.app.traversing.interfaces import TraversalError
from zope.app.folder import Folder
from zope.app.file import File
from zope.app.file.interfaces import IFile
from zope.app.container.interfaces import IContainer
from zope.app.publisher.browser import BrowserView

from wikification.browser.interfaces import IWikiPage

from kupusupport.adapters import html_body

from wikification.browser.utils import WikiPageInfo

class WikiPage(BrowserView) :
    """ A wiki page that 'wikifies' a container with ordinary HTML documents.
    
        See wikification/README.txt for a definition of what 
        'wikification' means and doctests of the methods of this class.
        
    """
    
    implements(IWikiPage)

    supported = 'text/html', 'application/xhtml+xml', 'application/xml', 'text/xml'
    
    def __init__(self, context, request) :
        super(WikiPage, self).__init__(context, request)
        
        self.container = self.getContainer()
        self.base = zapi.absoluteURL(self.container, request)
        self.title = u"Wiki page"
        

    def isAbsoluteLink(self, link) :
        for prefix in 'http:', 'ftp:', 'https:', 'mailto:' :
            if link.startswith(prefix) :
                return True
        return False
        
    def wikifyLink(self, link) :
        """ Modifies dead relative links and leaves
            all other links untouched.
        """
        
        if self.isAbsoluteLink(link) :
            return False, link
            
        path = link.split("/")
        try :
            zapi.traverse(self.container, path)
            return False, link
        except TraversalError :
            return True, self.base + "/createPage?path=" + "/".join(path)
 
 
    def wikify(self, body) :
        """ 
            Renders HTML with dead relative links as 'wikified' HTML,
            i.e. dead relative links are converted to links that
            enable the user to add new pages.
        """
    
        from wikification.parser import BaseHTMLProcessor
        
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
                                # modified.append(("class", "create-link"))
                                modified.append(("style", "color: red"))
                        modified.append((key, value))
  
                    BaseHTMLProcessor.unknown_starttag(self, tag, modified)
                else :
                    BaseHTMLProcessor.unknown_starttag(self, tag, attrs)               
 
        processor = LinkProcessor(self)
        processor.feed(body)
        return processor.output()
     
      
    def nextURL(self) :
        url = zapi.absoluteURL(self.context, self.request)
        return url + "/@@wiki"


class WikiContainerPage(WikiPage) :
    """ Wiki view for a container. """
    
    empty = File("""<html><body>No index.html found.</body></html>""", 
                        "text/html")
    
    def getContainer(self) :
        return self.context
        
    def getFile(self) :
        return self.context.get(u"index.html", self.empty)

    def renderBody(self) :
        
        file = self.getFile()
        return WikiFilePage(file, self.request).renderBody()

    def render(self):
        pass
        
        
class WikiFilePage(WikiPage) :
    """ Wiki view for a file. """
    
    def getContainer(self) :
        return self.context.__parent__
        
    def renderBody(self) :
        
        file = self.context

        if file.contentType in self.supported :
            body = html_body(file.data)
            #self.request.response.setHeader("Content-Type", "text/html")
            return self.wikify(body)
            
            #info = WikPageInfo(body, self.context, self.request, self.main)
       
        # file type not supported
        return "Sorry, not wikifiable at the moment."

    def __call__(self):
        page = WikiPageInfo(self.context, self.request) 
        return page.render()
        
class EditWikiPage(WikiFilePage) :

    def renderBody(self) :
        """ Shows a wikified version of the context. 
             
        """
        
        file = self.context
        body = html_body(file.data)
        #self.request.response.setHeader("Content-Type", "text/html")
        return self.wikify(body)
            
        #info = WikPageInfo(body, self.context, self.request, self.main)
        
        # not in supported content types

    def render(self):
        pass

    def saveText(self) :
        """
            Generic store method.           
        """
        request = self.request
        text = request.form.get("body")        
        self.file.data = text        
        request.response.redirect(self.nextURL())
    
    def getBody(self) :
        return html_body(self.file.data)
        
    #body = property(getBody)
    
   
class CreateWikiPage(WikiContainerPage) :

    def createFile(self) :
        """
            Creates a file at the given path. Creates all intermediate
            folders if necessary.
            
        """
               
        path = self.request.form['path'].split(u'/')
        
        assert len(path) > 0
        
        container = base = self.container
        for name in path[:-1] :
            try :
                container = zapi.traverseName(base, name)
                assert IContainer.providedBy(base)
            except TraversalError :
                container = base[name] = Folder()
            base = container
             
        if path[-1] in container :
            file = container[path[-1]]
        else :
            file = File()
            container[path[-1]] = file
        return file

    def saveText(self) :
        """
            Generic store method.           
        """
        request = self.request
        text = request.form.get("body")        
        file = self.createFile()
        file.data = text        
        request.response.redirect(self.nextURL())

