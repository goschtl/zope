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

$Id: wikipage.py 38895 2005-10-07 15:09:36Z dominikhuber $
"""
__docformat__ = 'restructuredtext'

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
from zorg.wikification.browser.interfaces import ILinkProcessor
from zorg.importer import IImporter
from zorg.kupusupport.adapters import html_body, get_title, get_description
from zorg.kupusupport.browser.views import KupuEditor as _KupuEditor
from zorg.kupusupport.interfaces import IKupuPolicy

from zorg.ajax.page import ComposedAjaxPage, PageElement
from zorg.restsupport import rest2html
from zorg.restsupport import html2rest


            
class WikiPage(ComposedAjaxPage) :
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
    add = "/@@wikiedit.html"
    uris = {
            'home': '#',
            'login': '#',
            }
    untitled = u"Untitled"

   
    def __init__(self, context, request, container=None) :
        """ Initializes some usefull instance variables. 
        
        
        """
        super(WikiPage, self).__init__(context, request)
          
        self.session = self.getSessionStorage()
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
        
        
    def verb(self) :
        """ Returns a descriptive verb. """
        return _('View')
        
    def getContainer(self) :
        """ Returns the base container. Should be overwritten. """
        return None
                           
    def wikify(self, body) :
        """ 
            Renders HTML with dead relative links as 'wikified' HTML,
            i.e. dead relative links are converted to links that
            enable the user to add new pages.
            
            >>> from zorg.wikification.tests import buildSampleSite
            >>> site = buildSampleSite()
            >>> request = TestRequest()
            >>> wiki = WikiPage(site, request)
            >>> html = '''<html><body>
            ... <a href="http://127.0.0.1/site/folder/wiki.html">Link</a>
            ... </body><html>'''
            
            
            >>> print wiki.wikify(html)
            <html><body>
            <a href="...wikiedit.html?add=wiki.html" class="wiki-link">Link</a>
            </body><html>
 
        
        """
        
        processor = ILinkProcessor(self)
        processor.feed(body)
        return processor.output()
     
      
    def nextURL(self) :
        url = zapi.absoluteURL(self.context, self.request)
        return url + self.action

        
class WikiContainerPage(WikiPage) :
    """ Wiki view for a container. """
    
    _noindex = ViewPageTemplateFile("./templates/noindex.pt")  
    _new = ViewPageTemplateFile("./templates/new.pt")
        
    untitled = u"Untitled Folder"
    
    
    def getContainer(self) :
        return self.context
        
    def isEmpty(self) :
        return not len(self.context)
        
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
            return self._new()
        else :
            return unicode(file.data, encoding="utf-8")
        
    def getFile(self) :
        return self.context.get(u"index.html")

    def getBody(self) :
        file = self.getFile()
        if file :
            page = WikiFilePage(file, self.request, self.getContainer())
            return page.getBody()
            
            
    def renderBody(self, debug=False) :
        """ Delegates the rendering to the WikiFilePage of the 
            index.html doocument.
            
        """
                
    #     file = self.getFile()
#         if file :
#             page = WikiFilePage(file, self.request, self.getContainer())
#             result = page.renderBody()
#             return result
        
 #        if debug :
#             import pdb; pdb.set_trace()
#             
        body = self.getBody()
        if body is not None :
            return self.wikify(unicode(body, encoding="utf-8"))
            
        return self._noindex()
       
        
class WikiFilePage(WikiPage) :
    """ Wiki view for a file. """
    
    untitled = u"Untitled Document"
    
    def isEmpty(self) :
        return False
        
    def getContainer(self) :
        return self.context.__parent__
        
    def getFile(self) :
        return self.context
        
    def getBody(self) :
        """ Returns the body as a unicode string. """
        file = self.context
        if file.contentType in self.supported :
            return html_body(file.data)
            
    def renderBody(self) :
        body = self.getBody()
        if body is not None :
            return self.wikify(unicode(body, encoding="utf-8"))
  
        return u"Sorry, not wikifiable at the moment."
            

class EditOptions(PageElement) :
    """ Allows the user to switch between Kupu, Rest and 
        other edit options. 
        
    """
    
    _choose = ViewPageTemplateFile("./templates/choose.pt")
            
    def render(self) :
        """ Allows the user to the select an editor editor. """
        return self._choose()        


class Editor(PageElement) :
    """ Base class for Editor page elements. """
 
    isType = "text/plain"
    asType = "text/plain"
    
    title = description = None

    def toHTML(self) :
        if self.isType == "text/plain" :
            return rest2html(self.data)
        elif self.isType == "text/html" :
            return self.data
        return _("unknown format: cannot convert file content. """)
        
    def toRest(self) :
        if self.isType == "text/plain" :
            return self.data
        elif self.isType == "text/html" :
            return html2rest(self.data) 
        return _("unknown format: cannot convert file content. """)
        
    def saveTo(self, file) :
        """ 
        Save method that stores the main content and sets
        the title and description if available.
        
        >>> from zope.app.file import File
        >>> from zorg.wikification.tests import buildSampleSite
        >>> site = buildSampleSite()
        >>> page = WikiEditor(site, TestRequest())
        >>> file = File()
        
        >>> editor = Editor(page)
        >>> editor.data = 'Some text'
        >>> editor.saveTo(file)
        >>> file.data
        'Some text'
        
        We can save in different formats :
        
        >>> editor.asType = "text/html"
        >>> editor.saveTo(file)
        >>> print file.data
        <p>Some text</p>
        
        """
        
        if self.asType is None :
            self.asType = file.contentType
        elif self.asType != file.contentType :
            file.contentType = self.asType
            
        if self.asType == "text/html" :
            data = self.toHTML()
        elif self.asType == "text/plain" :
            data = self.toRest()

        file.data = data
        
        dc = IZopeDublinCore(self.context)
        if self.title is not None :
            dc.title = self.title
        if self.description is not None :
            dc.description = self.description
        
        zope.event.notify(ObjectModifiedEvent(file))
        
    def editableHTML(self, html) :
        """ A method that extracts the editable HTML parts.
            Returns the body as a default that can be overwritten.
        """
        return html_body(html)
        
    def readFile(self, file) :
        """ Read method. 
        
        >>> editor = Editor(None)
        >>> from zope.app.file import File
        >>> file = File()
        >>> file.data = 'Some text'
        >>> file.contentType = 'text/plain'
        >>> print editor.readFile(file)
        Some text
        
        If the text type deviates from the stored one the text is
        converted automatically :
        
        >>> editor.isType = "text/html"
        >>> result = editor.readFile(file)
        >>> isinstance(result, unicode)
        True
        >>> print result
        <p>Some text</p>
        
        This works in both directions, from text to html and vice versa:
        
        >>> file.data = '<p>Some text</p>'
        >>> file.contentType = 'text/html'
        >>> print editor.readFile(file)
        <p>Some text</p>
        
        >>> editor.isType = "text/plain"
        >>> print editor.readFile(file)
        Some text
        
        """
        
        if self.isType is None :
            self.isType  = file.contentType
                 
        if self.isType == "text/html" :
        
            if file.contentType == "text/html" :
                html = self.editableHTML(file.data)
                return unicode(html, encoding="utf-8")
                
            if file.contentType == "text/plain" :
                return rest2html(file.data)
                
        elif self.isType == "text/plain" :
        
            if file.contentType == "text/html" :
                body = html_body(file.data)
                html = "<html><body>%s</body></html>" % body
                return unicode(html2rest(html), encoding="utf-8")
            if file.contentType == "text/plain" :
                return unicode(file.data, encoding="utf-8")   
        
        return _("unknown format: cannot show file content. """)
        
    
class RestEditor(Editor) :
    """ Main page element that shows a ReST editor. """
    
    _rest = ViewPageTemplateFile("./templates/rest.pt")

    def __init__(self, parent) :
        super(RestEditor, self).__init__(parent)
        
        self.data = parent.parameter('rest')
        self.title = parent.parameter('title')
        self.description = parent.parameter('description')
        
        self.isType = "text/plain"
        self.asType = "text/plain"
    
    def render(self) :
        """ Presents the rest editor to the user. """
        return self._rest()    


class TinyMCEEditor(Editor) :
    """ Main page element that shows a TineMCE editor. """
    
    _tinymce = ViewPageTemplateFile("./templates/tinymce.pt")

    def __init__(self, parent) :
        super(TinyMCEEditor, self).__init__(parent)
        
        self.data = parent.parameter('tinyhtml')
        self.title = parent.parameter('title')
        self.description = parent.parameter('description')
        
        self.isType = "text/html"
        self.asType = "text/html"
        
        print "TinyMCEEditor", self.data
        
    
    def render(self) :
        """ Presents the rest editor to the user. """
        return self._tinymce()    
  
          
class KupuEditor(Editor, _KupuEditor) :
    """ Main page element that shows the Kupu editor. """
    
    _kupu = ViewPageTemplateFile("./templates/kupu.pt")

    def __init__(self, parent) :
        super(KupuEditor, self).__init__(parent)
                
        self.data = self.parameter('kupu')
        self.isType = "text/html"
        self.asType = "text/html"
        
        if self.data :
            self.title = get_title(self.data)
            self.description = get_description(self.data)
                
    def editableHTML(self, html) :
        """ A method that extracts the editable HTML parts.
            Kupu uses the full data.
        """
        return html
        
    def render(self) :
        """ Presents the rest editor to the user. """
        return self._kupu()    
   
        
class WikiEditor(WikiPage) :   
    """ Base class for a wiki edit page. Provides methods that
        access and update file content.
        
        >>> from zorg.wikification.tests import buildSampleSite
        >>> site = buildSampleSite()
        >>> request = TestRequest("/", form=dict(rest="ReSt", editor="rest"))
        >>> page = WikiEditor(site, request)
        >>> page.main
        <zorg.wikification.browser.wikipage.RestEditor object at ...>

      
    """
   
    factory = dict(rest=RestEditor, kupu=KupuEditor, tinymce=TinyMCEEditor)
    chooser = EditOptions
    
    def __init__(self, context, request) :
        super(WikiEditor, self).__init__(context, request)  
        self.editor = self.parameter('editor', storage=self.session)
        self.main = self.factory.setdefault(self.editor, self.chooser)(self)
        self.main.asType = "text/html" # default: because we are using .html extension         


    def _modifyLink(self, cmd, link_id) :
        """ Help method that modified a link and saves the result into
            the file.
        """
        processor = ILinkProcessor(self)
        processor.command = cmd
        processor.link_id = link_id
        
        body = self.getBody()
        processor.feed(body)
        file = self.getFile()
        file.data = processor.output()
        
    def uploadFile(self, link_id) :
        """ Uploads a file for a wikified link and redirects 
            to the view again.
        """
        self._modifyLink('upload', link_id)
        self.request.response.redirect(self.nextURL())
        
        
    def modifyLink(self, cmd, link_id, verbose=True) :
        """ Modify a single link dynamically and return the new
            body.
        """
        self._modifyLink(cmd, link_id)
        return u'<div id="main">%s</div>' % self.renderBody()

      
class EditWikiPage(WikiEditor, WikiFilePage) :
    """ An edit view for wiki pages. """
    
    def verb(self) :
        return _('Edit')

    def editableTitle(self) :
        """ Returns the title that should be edited. """
        file = self.getFile()
        return IZopeDublinCore(file).title or u"Untitled"
                
    def display(self) :
        """ Returns the data that should be edited. """
        file = self.getFile()
        return self.main.readFile(file)
    
    def update(self, editor=None):
        """ Saves the edited content and redirects to the wiki view. """
        file = self.getFile()
        self.main.saveTo(file)
        self.request.response.redirect("wiki.html")
                
        
class EditWikiContainerPage(WikiContainerPage, EditWikiPage) :
    """ A specialization that edits the index.html if available. """ 

    def getExtraPath(self) :
        """ Returns the path that is added to the container if the user
            creates a new wiki page.
        """
        if self.isAddView() :
            filepath = self.request.form.get('add', '')
            return filepath.split(u'/')
        else :
            return ['index.html']
    
    def isAddView(self) :
        return self.request.form.get('add', None) is not None
        
    def verb(self) :
        if self.isAddView() :
            return _('Add')
        return _('Edit')

    def editableTitle(self) :
        """ Returns the title that should be edited. """
        if self.isAddView() :
            return u"Untitled"
        return IZopeDublinCore(self.getFile()).title
        
    def display(self) :
        """ Returns the data that should be edited. """
        if self.isAddView() :
            return self._new()
        return self.main.readFile(self.getFile())

    def createFile(self) :
        """
            Creates a file at the given path. Creates all intermediate
            folders if necessary.
            
        """        
        path = self.getExtraPath()

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
        file = self.createFile()
        self.main.saveTo(file)
        url = zapi.absoluteURL(file, self.request)
        request.response.redirect(url + self.action)

        

class CreateWikiPage(EditWikiContainerPage) :
    """ Creates a wiki page. """
 
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

    def display(self) :
        return self._new()
        

