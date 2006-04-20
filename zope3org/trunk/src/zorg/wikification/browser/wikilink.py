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

import re, urllib, cgi, os

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
            pattern = '<a class="wiki-link" href="%s">[%s]</a>'
        else :
            pattern = '<a class="wiki-link" href="%s">%s</a>'
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
            pattern = '<a href="%s" class="wiki-link"%s>'
            return pattern % (link, self._tagAttrs(attrs))
        else :
            pattern = '<a href="%s"%s>'
            return pattern % (link, self._tagAttrs(attrs))
            
            
    def afterCloseTag(self) :
        """ Handler that is called after a closed </a> tag.
            The default implementation returns None.
        """
        return None
        
    def postProcessing(self, html) :
        """ Handler for a postprocessing step. Called after a first
            pass with a preliminary html version.
            
            The default implementation returns the unmodified html
           
        """
        return html

    def editableLabel(self) :
        label = self.label.strip()
        if label.startswith('[') :
            label = label[1:]
        if label.endswith(']') :
            label = label[:-1]
        return label
        
    def unicodeLabel(self) :
        return unicode(self.editableLabel(), encoding='utf-8')
 
 
class BaseLinkProcessor(BaseHTMLProcessor) :
    """ Implements a processor that is able to visit and modify all links. 
    """
    
    absolute_prefixes = 'http:', 'ftp:', 'https:', 'mailto:'
         
    link_refs = dict(a='href', img='src')       # treat 'a href' and 'img src'

    _url = r'''(?=[a-zA-Z0-9./#])    # Must start correctly
                  ((?:              # Match the leading part
                      (?:ftp|https?|telnet|nntp) #     protocol
                      ://                        #     ://
                      (?:                       # Optional 'username:password@'
                          \w+                   #         username
                          (?::\w+)?             #         optional :password
                          @                     #         @
                      )?                        # 
                      [-\w]+(?:\.\w[-\w]*)+     #  hostname (sub.example.com)
                  )                             #
                  (?::\d+)?                     # Optional port number
                  (?:                           # Rest of the URL, optional
                      /?                                # Start with '/'
                      [^.!,?;:"'<>()\[\]{}\s\x7F-\xFF]* # Can't start with these
                      (?:                               #
                          [.!,?;:]+                     #  One or more of these
                          [^.!,?;:"'<>()\[\]{}\s\x7F-\xFF]+  # Can't finish
                          #'"                           #  # or ' or "
                      )*                                #
                  )?)                                   #
               '''

    _email = r'''(?:mailto:)?            # Optional mailto:
                    ([-\+\w]+               # username
                    \@                      # at
                    [-\w]+(?:\.\w[-\w]*)+)  # hostname
                 '''
    
    url_link = re.compile(_url, re.VERBOSE)
    email_link = re.compile(_email, re.VERBOSE)
    text_link = re.compile('\[.*?\]', re.VERBOSE)


    def reset(self):
        BaseHTMLProcessor.reset(self)
        self.traversed = {}
   
    def isAbsoluteURL(self, link) :
        """ Returns true if the link is a complete URL. 
            
            Note that an absolute URL in this sense 
            might point to a local object.
        """
        
        for prefix in self.absolute_prefixes  :
            if link.startswith(prefix) :
                return True
        return False

    def onRelativeLink(self, link) :
        """ Event handler that can be specialized. """
        return link
        
    def onWikiTextLink(self, link) :
        """ Event handler that can be specialized. """
        return link

    def onAbsoluteLink(self, link) :
        """ Event handler that can be specialized. """
        return link

    def traverseLink(self, node, link) :
        """ Help method that follows a relative link from a context node. """
        remaining = urllib.unquote(link)
        if link in self.traversed :
            return self.traversed[link]
        path = [x for x in remaining.split("/") if x]        
        while path :         
            try :
                name = path[0]
                name = unicode(name, encoding='utf-8')
                node = zapi.traverseName(node, name)
                name = path.pop(0)
            except (TraversalError, UnicodeEncodeError) :
                break
        self.traversed[link] = node, path
        return node, path

    def handle_data(self, text) :
        """ Called for each text block. Extracts wiki text links. """
        
        text = re.sub(self.url_link, r'''<a href="\1">\1</a>''', text)
        text = re.sub(self.email_link, r'''<a href="mailto:\1">\1</a>''', text)
        
        result = ""
        end = 0
        for m in self.text_link.finditer(text):
            
            start = m.start()
            result += text[end:start]
            end = m.end()
            between = text[start+1:end-1]
            result += self.onWikiTextLink(between)           
        result += text[end:]       
        
        self.pieces.append(result)
        
        
    def unknown_starttag(self, tag, attrs):
        """ Called for each tag. Calls link event handlers. """
        
        if tag in self.link_refs :
            result = []
            for key, value in attrs :
                if key == self.link_refs[tag] :
                    if self.isAbsoluteURL(value) :
                        value = self.onAbsoluteLink(value)
                    else :
                        value = self.onRelativeLink(value)
                result.append((key, value))
           
            BaseHTMLProcessor.unknown_starttag(self, tag, result) 
            return True
     
        BaseHTMLProcessor.unknown_starttag(self, tag, attrs)               



class RelativeLinkProcessor(BaseLinkProcessor) :
    """ Implements a processor that converts all relative links
        into absolute ones. 
     
        >>> html = '''<p><a href="http://www.iwm-kmrc.de">Absolute</a></p>
        ...           <p><a href="relative">Relative</a></p>'''
        
        >>> processor = RelativeLinkProcessor("http://www.iwm-kmrc.de")
        >>> processor.feed(html)
        >>> print processor.output()
        <p><a href="http://www.iwm-kmrc.de">Absolute</a></p>
        <p><a href="http://www.iwm-kmrc.de/relative">Relative</a></p>
       
        
    """
 
    def __init__(self, base_url) :
        BaseHTMLProcessor.__init__(self)
        self.base_url = base_url
        
    def onRelativeLink(self, link) :
        """ Event handler that can be specialized. """
        return "%s/%s" % (self.base_url, link)
        
        
class WikiLinkProcessor(BaseLinkProcessor) :
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
        >>> processor = WikiLinkProcessor(page)
        
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
        elif self.isAbsoluteURL(link) :
            return False, link
        elif link.startswith("#") :
            return False, link
        else :
            node = page.container
             
        node, path = self.traverseLink(node, link)
        if path :
            return True, self.absoluteAddLink(node, path)

        if IFile.providedBy(node) :
            if node.contentType not in page.supported :
                return False, self.absoluteLink(node)
                                
        return False, self.absoluteWikiLink(node)

        
    def absoluteWikiLink(self, node) :
        return zapi.absoluteURL(node, self.page.request) + self.page.action

        
    def absoluteAddLink(self, node, path) :
        url = zapi.absoluteURL(node, self.page.request)
        appendix = urllib.urlencode({'add': "/".join(path)})
        return  url + self.page.add + "?" + appendix


    def absoluteLink(self, node) :
        return zapi.absoluteURL(node, self.page.request)
         
         
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
        
        >>> link_processor = WikiLinkProcessor(page)
        >>> link_processor.handle_data('A [link]')
        >>> link_processor.pieces
        ['A <a class="wiki-link" href="...@@wikiedit.html?add=link">[link]</a>']

        
        >>> link_processor = WikiLinkProcessor(page)
        >>> link_processor.handle_data('A [link] and [another one]')
        >>> link_processor.pieces
        ['A <a ...>[link]</a> and <a ...>[another one]</a>']
        
        This method also converts urls and email addresses into clickable links:
        
        >>> link_processor = WikiLinkProcessor(page)
        >>> link_processor.handle_data('Test mailto:jim@zope.org')
        >>> link_processor.pieces
        ['Test <a href="mailto:jim@zope.org">jim@zope.org</a>']
        
        >>> link_processor = WikiLinkProcessor(page)
        >>> link_processor.handle_data('Test http://www.iwm-kmrc.de')
        >>> link_processor.pieces
        ['Test <a href="http://www.iwm-kmrc.de">http://www.iwm-kmrc.de</a>']
        
        """
                 
        if self.placeholder is not None :
            self.placeholder.label += text
            self.pieces.append(text)
            return
            
        BaseLinkProcessor.handle_data(self, text)
             
    def onWikiTextLink(self, label) :
        name = label.replace(" ", "")
        placeholder = self.createPlaceholder(label, name)
        self.placeholder = None
        return placeholder.textLink()
        
    def output(self) :
        """ Returns the processing result.
        
        Adds an additional postprocessing step 
        for placeholder commands with global scope.
        
        """
        
        html = BaseHTMLProcessor.output(self)
        for placeholder in self.placeholders.values() :
            html = placeholder.postProcessing(html)
        return html
        
        
class MenuPlaceholder(Placeholder) :
    """ A placeholder, that offers various edit options for the user.
    Placeholders are created by the link processor on demand and are referenced
    by a index based id:
    
    >>> from zorg.wikification.tests import buildSampleSite
    >>> from zorg.wikification.browser.wikipage import WikiPage
    >>> site = buildSampleSite()
    
    >>> page = WikiPage(site, TestRequest())
    >>> processor = WikiLinkProcessor(page)    
    >>> placeholder1 = processor.createPlaceholder("Label", "http://link")
    >>> placeholder1.index
    0
    >>> placeholder2 = processor.createPlaceholder("Label", "http://link")
    >>> placeholder2.index
    1
    
    """
    
    _menu = ViewPageTemplateFile("./templates/linkmenu.pt")
    _link = '<a class="wiki-link" href="%s" onmouseover="%s" onmouseout="%s" %s>'
    _dimmed = '<span class="dimmed-wiki-link">'
    
    wikified = False
    outdated = False
    enabled = True
    
    def __init__(self, processor, index, label, link) :
        super(MenuPlaceholder, self).__init__(processor, index, label, link)
        self.enabled = processor.page.isEditable()
        self.menu_id = processor.createMenuId(index)
        self.onMouseOver = "PopupMenu.update(this, '%s');" % self.menu_id
        self.onMouseOut = "PopupMenu.leave(this, '%s');" % self.menu_id
       
    def startTag(self, attrs) :
        """ Called when a starttag for a placeholder is detected. """
        
        wikified, link = self.processor.wikifyLink(self.link)
        self.link = link
        if wikified :
            self.wikified = True
            attrs.append(("id", self.link_id))
            if self.enabled :
                return self._link % (link, self.onMouseOver, self.onMouseOut,
                                                        self._tagAttrs(attrs))
            else :
                return self._dimmed
        else :
            pattern = '<a href="%s"%s>'
            return pattern % (self.link, self._tagAttrs(attrs))
        
    def textLink(self) :
        start = self.startTag([])
        menu = self.afterCloseTag() or ''
        if self.wikified :
            if self.enabled :
                return "%s[%s]</a>%s" % (start, self.label, menu)
            else :
                return "[%s]</span>" % self.label
        else :
            return "%s%s</a>%s" % (start, self.label, menu)
            
    def afterCloseTag(self) :
        if self.wikified :
            return '<span id="outer%s"></span>' % self.menu_id
            menu = self._menu()
            return menu.encode("utf-8")
        return None
                

class SavingPlaceholder(Placeholder) :
    """ A placeholder that saves the result to disk. 
    
        Determines whether a change is performed globally or only
        at the position of the placeholder.
        
    """
    
    global_scope = False        # default: depends on usecase
    
    def startTag(self, attrs) :
        """ Called when a starttag for a placeholder is detected. """
        pattern = '<a href="%s"%s>'
        print "Saving", attrs
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
    
    new_link = None
    
    def addObject(self) :
        """ Main method that adds the object and returns the new url.
            Must be specialized.
        """
        pass
    
    def generateAppendix(self, num, type=None) :
        """ Returns '001', '002' etc. as an automatically generated
            appendix for link targets."""
        return "%03d" % num
            
    def generateName(self, name, container) :
        """ Generates a new name that includes a generated appendix. """
        basename, extension = os.path.splitext(name)
        id = 1
        while (basename + self.generateAppendix(id) + extension) in container :
            id=id+1
        return basename + self.generateAppendix(id) + extension
    
    def _addObject(self, name, obj) :
        """ Help method that adds an object and returns the new name. 
        
            Handles also the case that the user wants to limit
            the new link to the clicked one.
            
            XXX This first implementation is a hack and needs reworking
            
        
        """
        
        zope.event.notify(ObjectCreatedEvent(obj))
        
        scope = self.page.parameter('scope')
        self.global_scope = scope and scope.lower() == 'on'
        
        container = self.page.container
        chooser = INameChooser(container)
        name = chooser.chooseName(name, obj)
        
        if not self.global_scope :
            name = self.generateName(name, container)
            
        container[name] = obj
        contained = container[name]
        
        title = self.page.parameter('title')
        description = self.page.parameter('description')
        
        dc = IZopeDublinCore(obj)
        if title :
            dc.title = title
        if description :
            dc.description = description
        
        return name.encode("utf-8")
        
    def textLink(self) :
        name = self.addObject()
        self.new_link = '<a href="%s">%s</a>' % (name, self.editableLabel())
        return self.new_link
        
    def startTag(self, attrs) :
        name = self.addObject()
        pattern = '<a href="%s"%s>'
        return pattern % (name, self._tagAttrs(attrs))

    def postProcessing(self, html) :
        """ Replaces a textual WikiLink globally. """
        if self.global_scope and self.new_link :
            html = html.replace("[%s]" % self.label, self.new_link)
        return html
        
        
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
    

class CreatePagePlaceholder(AddObjectPlaceholder) :
    """ A placeholder for a new single page. Note that this command only
        changes the reference of the clicked link. Thus you can have
        several links with the same name and different URLs.
    """
                
    def addObject(self) :
        """ Create a page. Returns the name of the new page.
        """
        
        label = self.editableLabel()
        contenttype = "text/html"
        name = self.page.parameter('name')
        return self._addObject(name, File(u'New Page', contenttype))


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

class AjaxLinkProcessor(WikiLinkProcessor) :
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
    
     
