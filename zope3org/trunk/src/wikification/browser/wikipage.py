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

import re, urllib

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

from zope.publisher.browser import TestRequest

from wikification.browser.interfaces import IWikiPage

from kupusupport.adapters import html_body
from kupusupport.browser.views import KupuEditor
from kupusupport.interfaces import IKupuPolicy

class WikiPage(BrowserView) :
    """ A wiki page that 'wikifies' a container with ordinary HTML documents.
    
        See wikification/README.txt for a definition of what 
        'wikification' means and doctests of the methods of this class.
    
        >>> from wikification.tests import buildSampleSite
        >>> site = buildSampleSite()
        >>> page = WikiPage(site, TestRequest())
         
    """
    
    implements(IWikiPage)

    supported = 'text/html', 'application/xhtml+xml', 'application/xml', 'text/xml'
    title = u"Wiki page"
    action = "/@@wiki.html"      # the action that wikifies
    add = "/@@kupuadd.html"
    uris = {
            'home': '#',
            'login': '#',
            }
    
    contact_form = {
            'action_url': '#',
            }
            
   
    def __init__(self, context, request, container=None) :
        """ Initializes some usefull instance variables. 
        
        
        """
        super(WikiPage, self).__init__(context, request)
          
        self.macros = {}
        if container is None :
            self.container = self.getContainer() or context
        else :
            self.container = container
        self.base = zapi.absoluteURL(self.container, request)
        site = self.site = IPhysicallyLocatable(self.container).getNearestSite()
           
        dc = IZopeDublinCore(self.context)
        self.dc = dc
        
        self.title = dc.Title() or 'Untitled'
        self.site_title = IZopeDublinCore(site).title or U'No site title'
        self.html_title = self.getHTMLTitle
        self.language = dc.Language()
       
    def getHTMLTitle(self):
        if self.title and self.site_title:
            if self.title != self.site_title:
                return '%s - %s' % (self.title, self.site_title)
        return self.title or self.site_title 
        
    def isAbsoluteLink(self, link) :
        for prefix in 'http:', 'ftp:', 'https:', 'mailto:' :
            if link.startswith(prefix) :
                return True
        return False
        
    def getContainer(self) :
        """ Returns the base container. Should be overwritten. """
        return None
        
    def wikifyLink(self, link) :
        """ Modifies dead relative links and leaves
            all other links untouched.
        """
        
        site_url = zapi.absoluteURL(self.site, self.request)
        if link.startswith(site_url) :
            link = link[len(site_url)+1:]
        elif self.isAbsoluteLink(link) :
            return False, link
            
        path = link.split("/")
        try :
            zapi.traverse(self.container, path)
            return False, self.base + "/" + link + self.action
        except TraversalError :
            appendix = urllib.urlencode({'path': "/".join(path)})
            return True, self.base + self.add + "?" + appendix
 
 
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
    
    def getContainer(self) :
        return self.context
        
    def getContent(self) :
        """ Returns the editable content of a container.
        
            Returns the content of index.html if available
            or a dummy message otherwise.
            
            >>> from wikification.tests import buildSampleSite
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


        
class EditWikiPage(KupuEditor, WikiFilePage) :
 
     # implementation of kupusupport.IKupuPolicy
    def update(self, kupu=None):
        """ Overwrites KupuEditor.update with a new redirect. """
        
        if kupu:
            policy = IKupuPolicy(self.context)
            policy.update(kupu)
            zope.event.notify(ObjectModifiedEvent(self.context))

        self.request.response.redirect("wiki.html")



class CreateWikiPage(KupuEditor, WikiContainerPage) :

    def createFile(self) :
        """
            Creates a file at the given path. Creates all intermediate
            folders if necessary.
            
        """
        
        filepath = self.request.form.get('path', 'index.html')
        path = filepath.split(u'/')

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
            zope.event.notify(ObjectCreatedEvent(file))
            container[path[-1]] = file
        return file

    def update(self, kupu=None):
        """
            Generic store method.           
        """
        request = self.request
        file = self.createFile()
        file.contentType = "text/html"
        file.data = kupu
        zope.event.notify(ObjectModifiedEvent(file))
        request.response.redirect(self.nextURL())

