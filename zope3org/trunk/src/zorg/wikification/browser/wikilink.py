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

$Id: wikilink.py 38895 2005-10-07 15:09:36Z dominikhuber $
"""
__docformat__ = 'restructuredtext'

import re, urllib, cgi

import zope

from zope.interface import implements
from zope.component import adapts
from zope.app import zapi
from zope.app import contenttypes
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.dublincore.interfaces import IZopeDublinCore
from zope.app.file import File
from zope.app.folder import Folder
from zope.app.file.interfaces import IFile
from zope.app.event.objectevent import ObjectCreatedEvent
from zope.app.container.interfaces import INameChooser
from zope.app.traversing.interfaces import TraversalError
from zope.publisher.browser import TestRequest

from zorg.ajax.page import PageElement
from zorg.wikification.parser import BaseHTMLProcessor
from zorg.wikification.browser.interfaces import IWikiPage
from zorg.wikification.browser.interfaces import ILinkProcessor

class Placeholder(PageElement) :
    """ A base placeholder that renders a wikified link without id but
        with a special css.
    """
    
    def __init__(self, processor, index, label, link) :
        super(Placeholder, self).__init__(processor.page)
        self.processor = processor
        self.page = processor.page
        self.index = index
        self.label = label
        if self.label :                 # with a label we are in text mode
                                        # and it's up to the user to provide
                                        # an additional upload target name
            self.upload_name = ""
        else :
            self.upload_name = link
        self.link = link
        self.link_id = processor.createLinkId(index)
        self.nested = 0
 
    def textLink(self) :
        wikified, link = self.processor.wikifyLink(self.link)
        if wikified :
            pattern = u'<a class="wiki-link" href="%s">[%s]</a>'
        else :
            pattern = u'<a class="wiki-link" href="%s">%s</a>'
        return pattern % (link, self.label)
   
    def _tagAttrs(self, attrs) :
        result = ""
        for key, value in attrs :
            if key.lower() not in ("class", "href") :
                result += ' %s="%s"' % (key, value)
        return result
                
    def startTag(self, attrs) :
        """ Called when a starttag for a placeholder is detected. """
     
        wikified, link = self.processor.wikifyLink(self.link)
        if wikified :
            pattern = u'<a href="%s" class="wiki-link"%s>'
            return pattern % (link, self._tagAttrs(attrs))
        else :
            pattern = u'<a href="%s"%s>'
            return pattern % (link, self._tagAttrs(attrs))
            
            
    def afterCloseTag(self) :
        """ Handler that is called after a closed </a> tag.
            The default implementation returns None.
        """
        return None

    def editableLabel(self) :
        label = self.label.strip()
        if label.startswith('[') :
            label = label[1:]
        if label.endswith(']') :
            label = label[:-1]
        return label
        
        
class BaseLinkProcessor(BaseHTMLProcessor) :
    """ A link processor that wikifies the links by modifying the
        href and other attributes of a link.
        
    """
    
    implements(ILinkProcessor)
    adapts(IWikiPage)
        
    command = None
    
    def __init__(self, page) :
        BaseHTMLProcessor.__init__(self)
        self.page = page
        self.placeholders = {}
        self.placeholder = None     # current placeholder
        
    def createLinkId(self, index) :
        return "wiki-link%s" % index
        
    def createMenuId(self, index) :
        return "wiki-menu%s" % index
       
    def createPlaceholder(self, label, link, factory=Placeholder) :
        """
        Creates a placeholder page element and stores it for later
        access in a dict with placeholder ids as keys and the placeholders
        as values.
        """
        index = len(self.placeholders)
        placeholder = factory(self, index, label, link)
        self.placeholders[placeholder.link_id] = placeholder
        self.placeholder = placeholder
        return placeholder        
        
    def isAbsoluteURL(self, link) :
        """ Returns true if the link is a complete URL. 
            
            Note that an absolute URL in this sense 
            might point to a local object.
        """
        
        for prefix in 'http:', 'ftp:', 'https:', 'mailto:' :
            if link.startswith(prefix) :
                return True
        return False

    def wikifyLink(self, link) :
        """
        Modifies dead relative links and leaves all other links untouched.
        
        Returns a tuple of a boolean indicating a modification and the 
        resulting link.
                
        >>> from zorg.wikification.tests import buildSampleSite
        >>> site = buildSampleSite()
        >>> request = TestRequest()
        >>> from zorg.wikification.browser.wikipage import WikiPage
        >>> page = WikiPage(site, request)
        >>> processor = BaseLinkProcessor(page)
        
        Anchors and absolute external links are left unmodified :
        
        >>> processor.wikifyLink('#anchor')
        (False, '#anchor')
        >>> processor.wikifyLink('http://www.zope.org')
        (False, 'http://www.zope.org')
        
        Links to wikifiable objects are converted to links with wiki views:
        
        >>> processor.wikifyLink('http://127.0.0.1/site/index.html')
        (False, 'http://127.0.0.1/site/index.html/@@wiki.html')
        
        >>> processor.wikifyLink('http://127.0.0.1/site/folder')
        (False, 'http://127.0.0.1/site/folder/@@wiki.html')
        
        Relative and internal absolute links are treated the same. If 
        a link can be traversed successfully only the specific wiki
        view is added to ensure that we remain in the wiki navigation :
       
        >>> processor.wikifyLink('http://127.0.0.1/site')
        (False, 'http://127.0.0.1/site/@@wiki.html')
        >>> processor.wikifyLink('http://127.0.0.1/site/folder/emptysubfolder')
        (False, 'http://127.0.0.1/site/folder/emptysubfolder/@@wiki.html')
        
        If the path cannot completely be resolved the link is changed to
        an add view call :
        
        >>> processor.wikifyLink('http://127.0.0.1/site/folder/wikify.html')
        (True, 'http://127.0.0.1/site/folder/@@wikiedit.html?add=wikify.html')
        
        >>> processor.wikifyLink('http://127.0.0.1/site/folder/emptysubfolder/b')
        (True, 'http://127.0.0.1/site/folder/emptysubfolder/@@wikiedit.html?add=b')
        
        
        """
        
        page = self.page
        site_url = zapi.absoluteURL(page.site, page.request)
        if link.startswith(site_url) :
            link = link[len(site_url)+1:]
            node = page.site
            url = site_url
        elif self.isAbsoluteURL(link) :
            return False, link
        elif link.startswith("#") :
            return False, link
        else :
            node = page.container
            url = zapi.absoluteURL(node, page.request)
        
        remaining = urllib.unquote(link)
        path = [x for x in remaining.split("/") if x]        
        while path :         
            try :
                name = path[0]
                node = zapi.traverseName(node, name)
                url += "/" + name
                name = path.pop(0)
            except TraversalError :
                break
        
        if path :
            appendix = urllib.urlencode({'add': "/".join(path)})
            return True, url + page.add + "?" + appendix

        if IFile.providedBy(node) :
            if node.contentType not in page.supported :
                return False, zapi.absoluteURL(node, page.request)
            else :
                url = zapi.absoluteURL(node, page.request)
                               
        return False, url + page.action
         
         
    def unknown_starttag(self, tag, attrs):
        """ Called for each tag. Wikifies links. """
        
        if self.placeholder is None :
            if tag == "a" :
                href = ""
                others = []
                for key, value in attrs :
                    if key == "href" :
                        href = value
                    else :
                        others.append((key, value))
                self.createPlaceholder("", href)
                self.pieces.append(self.placeholder.startTag(others))
                return True
        else :
            self.placeholder.nested += 1
            
        BaseHTMLProcessor.unknown_starttag(self, tag, attrs)               

    def unknown_endtag(self, tag) :
        """ Called for each tag. Looks for pending placeholders and
            asks the existing placeholder for additional HTML that
            is rendered after the tag is closed.
        """
        
        BaseHTMLProcessor.unknown_endtag(self, tag)
        if self.placeholder is not None :
            if self.placeholder.nested == 0 :
                after = self.placeholder.afterCloseTag()
                if after is not None :
                    self.pieces.append(after)
                self.placeholder = None
            else :
                self.placeholder.nested -= 1
            
        
    def handle_data(self, text):
        """
        Called for each block of plain text, i.e. outside of any tag and
        not containing any character or entity references.
              
        >>> from zorg.wikification.tests import buildSampleSite
        >>> site = buildSampleSite()
        >>> from zorg.wikification.browser.wikipage import WikiPage
        >>> page = WikiPage(site, TestRequest())
        
        >>> link_processor = BaseLinkProcessor(page)
        >>> link_processor.handle_data('A [link]')
        >>> link_processor.pieces
        [u'A <a class="wiki-link" href="...@@wikiedit.html?add=link">[link]</a>']

        
        >>> link_processor = BaseLinkProcessor(page)
        >>> link_processor.handle_data('A [link] and [another one]')
        >>> link_processor.pieces
        [u'A <a ...>[link]</a> and <a ...>[another one]</a>']
        
        
        """
        
        if self.placeholder is not None :
            self.placeholder.label += text
            self.pieces.append(text)
            return

        text_link = re.compile('\[.*?\]', re.VERBOSE)
        
        result = ""
        end = 0
        for m in text_link.finditer(text):
            
            start = m.start()
            result += text[end:start]
            end = m.end()
            between = text[start+1:end-1]
            
            name = between.replace(" ", "")
            placeholder = self.createPlaceholder(between, name)
            result += placeholder.textLink()
            self.placeholder = None
            
        result += text[end:]
        self.pieces.append(result)
        

          
class MenuPlaceholder(Placeholder) :
    """ A placeholder, that offers various edit options for the user.
    Placeholders are created by the link processor on demand and are referenced
    by a index based id:
    
    >>> from zorg.wikification.tests import buildSampleSite
    >>> from zorg.wikification.browser.wikipage import WikiPage
    >>> site = buildSampleSite()
    
    >>> page = WikiPage(site, TestRequest())
    >>> processor = BaseLinkProcessor(page)    
    >>> placeholder1 = processor.createPlaceholder(u"Label", "http://link")
    >>> placeholder1.index
    0
    >>> placeholder2 = processor.createPlaceholder(u"Label", "http://link")
    >>> placeholder2.index
    1
    
    """
    
    _menu = ViewPageTemplateFile("./templates/linkmenu.pt")
    _link = '<a class="wiki-link" href="%s" onmouseover="%s" onclick="return clickreturnvalue()"%s>'
    
    wikified = False
    
    def __init__(self, processor, index, label, link) :
        super(MenuPlaceholder, self).__init__(processor, index, label, link)
        self.menu_id = processor.createMenuId(index)
        
        self.onMouseOver = "dropdownlinkmenu(this, event, '%s');" % self.menu_id
       
    def startTag(self, attrs) :
        """ Called when a starttag for a placeholder is detected. """
        
        wikified, link = self.processor.wikifyLink(self.link)
        self.link = link
        if wikified :
            self.wikified = True
            attrs.append(("id", self.link_id))
            return self._link % (link, self.onMouseOver, self._tagAttrs(attrs))
        else :
            pattern = u'<a href="%s"%s>'
            return pattern % (self.link, self._tagAttrs(attrs))
        
    def textLink(self) :
        start = self.startTag([])
        menu = self.afterCloseTag() or ''
        if self.wikified :
            return "%s[%s]</a>%s" % (start, self.label, menu)
        else :
            return "%s%s</a>%s" % (start, self.label, menu)
            
    def afterCloseTag(self) :
        if self.wikified :
            menu = self._menu()
            return menu.encode("utf-8")
        return None
                

class SavingPlaceholder(Placeholder) :
    """ A placeholder that saves the result to disk. """
    
    def startTag(self, attrs) :
        """ Called when a starttag for a placeholder is detected. """
        pattern = u'<a href="%s"%s>'
        return pattern % (self.link, self._tagAttrs(attrs))

class RenamedPlaceholder(SavingPlaceholder) :
    """ A placeholder with a changed label. """
    
    fired = False
            
    def textLink(self) :
        """ Replaces the label in text mode. """
        
        label = self.page.parameter("label").encode("utf-8")
        self.fired = True
        return '[' + label + ']'
        
    def afterCloseTag(self) :
        """ Replaces the label after the tag has been closed. """
        
        if self.nested == 0 and not self.fired :
            label = self.page.parameter("label").encode("utf-8")
            self.processor.pieces[-2] = label
            
        

 
class AddObjectPlaceholder(SavingPlaceholder) :
    """ A convenient base class for placeholders that add objects. """
    
    def addObject(self) :
        """ Main method that adds the object and returns the new url.
            Must be specialized.
        """
        pass
    
    
    def _addObject(self, name, obj) :
        """ Help method that adds an object and returns the new name. """
        
        zope.event.notify(ObjectCreatedEvent(obj))
        
        container = self.page.container
        chooser = INameChooser(container)
        name = chooser.chooseName(name, obj)
        container[name] = obj
        contained = container[name]
        
        title = self.page.parameter('title')
        description = self.page.parameter('description')
        
        dc = IZopeDublinCore(obj)
        if title :
            dc.title = title
        if description :
            dc.description = description
         
        return name # zapi.absoluteURL(contained, self.page.request)
        
    def textLink(self) :
        name = self.addObject()
        return '<a href="%s">%s</a>' % (name, self.editableLabel())
        
    def startTag(self, attrs) :
        name = self.addObject()
        pattern = u'<a href="%s"%s>'
        return pattern % (name, self._tagAttrs(attrs))

        
class UploadFilePlaceholder(AddObjectPlaceholder) :
    """ A placeholder that points to an uploaded file. """
    
    def addObject(self) :
        """ Upload a file. Returns the name of the new file.
        """
        
        label = self.editableLabel()
        data = self.page.parameter('data')
        contenttype = self.page.parameter('contenttype')

        filename = self.filename("data", label)
        name = self.page.parameter('name') or unicode(filename, encoding="utf-8")

        if not contenttype :
            contenttype = contenttypes.guess_content_type(filename)[0]
     
        return self._addObject(name, File(data, contenttype))
        
 
class CreateFolderPlaceholder(AddObjectPlaceholder) :
    """ A placeholder that points to a new folder. """
    
    def addObject(self) :
        """ Creates a new folder. Returns the name of the folder.
        """
        
        label = self.editableLabel()
        name = self.page.parameter('name') or unicode(label, encoding="utf-8")
        
        return self._addObject(name, Folder())
    

class CreatePagePlaceholder(Placeholder) :
    pass

class NoopPlaceholder(Placeholder) :
    """ An unmodified placeholder. """
    
    def textLink(self) :
        return "[%s]" % self.label
     
    def startTag(self, attrs) :
        if self.link.endswith(self.page.action) :
            link = self.link[:-len(self.page.action)]
        else :
            link = self.link
        return '<a href="%s">' % (link)

class AjaxLinkProcessor(BaseLinkProcessor) :
    """ A link processor that wikifies the links by modifying the
        href of a link and additionally inserting a javascript based menu
        that allows the user to choose an edit option. 
    """
               
    cmds = dict(rename=RenamedPlaceholder, 
                        upload=UploadFilePlaceholder,
                        folder=CreateFolderPlaceholder,
                        newpage=CreatePagePlaceholder)

    command = None      # the name of the link modification command
    link_id = None
    
    
    def createPlaceholder(self, label, link, factory=MenuPlaceholder) :
        """
        Creates a placeholder page element and stores it for later
        access in a dict with placeholder ids as keys and the placeholders
        as values.
        """
        
        index = len(self.placeholders)
       
        if self.command :
            if self.link_id == self.createLinkId(index) :
                factory = self.cmds[self.command]
                placeholder = factory(self, index, label, link)
            else :
                placeholder = NoopPlaceholder(self, index, label, link)
        else :
            placeholder = factory(self, index, label, link)
        self.placeholders[placeholder.link_id] = placeholder
        self.placeholder = placeholder
        return placeholder            
    
     
