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

import re
from zope.app import zapi
from zope.interface import implements
from zope.app.traversing.interfaces import TraversalError
from zope.app.folder import Folder
from zope.app.file import File
from zope.app.file.interfaces import IFile
from zope.app.container.interfaces import IContainer
from zope.app.publisher.browser import BrowserView

from wikification.browser.interfaces import IWikiPage

def html_body(html) :

    output = re.compile('<body.*?>(.*?)</body>', re.DOTALL | re.IGNORECASE).findall(html)
    if len(output) > 1 :
        print "Warning: more than one body tag."
    elif len(output) == 0 :     # hmmh, a html fragment?
        return html  
    return output[0]
    

class WikiPage(BrowserView) :
    """ A wiki page that 'wikifies' a container with ordinary HTML documents.
    
        See wikification/README.txt for a definition of what 
        'wikification' means and doctests of the methods of this class.
        
    """
    
    editable = False
    supported = 'text/html', 'application/xhtml+xml', 'application/xml', 'text/xml'
    
    implements(IWikiPage)
    
       
    def __init__(self, context, request) :
        super(WikiPage, self).__init__(context, request)
        
        self.container = self.getContainer()
        self.file = self.getFile()
        self.base = zapi.absoluteURL(self.container, request)

    def wiki(self) :
        """ Shows a wikified version of the context. 
             
        """
        
        file = self.getFile()
        if file.contentType in self.supported :
            if self.editable :
                body = html_body(file.data)
            else :
                body = file.data
            self.request.response.setHeader("Content-Type", "text/html")
            return self.render(body)
        
        return "Sorry, not wikifiable at the moment."
       

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
 
 
    def render(self, body) :
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
        if self.create :
            file = self.createFile()
        else :
            file = self.file
        file.data = text        
        request.response.redirect(self.nextURL())

    def nextURL(self) :
        url = zapi.absoluteURL(self.context, self.request)
        return url + "/@@wiki"


        
class WikiContainerPage(WikiPage) :
    """ Wiki view for a container. """
    
    empty = File("""<html><body>Sorry, explanations later.</body></html>""", 
                        "text/html")
    
    def getContainer(self) :
        return self.context
        
    def getFile(self) :
        return self.context.get(u"index.html", self.empty)
        
        
class WikiFilePage(WikiPage) :
    """ Wiki view for a file. """
    
    def getContainer(self) :
        return self.context.__parent__
        
    def getFile(self) :
        return self.context
        
        
class EditWikiPage(WikiFilePage) :

    editable = True
    create = False
    
    def getBody(self) :
        return html_body(self.file.data)
        
    body = property(getBody)
    
   
class CreateWikiPage(WikiContainerPage) :

    editable = True
    create = True
    
    body = u""
    
    