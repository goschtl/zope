import re
from zope.app import zapi
from zope.interface import implements
from zope.app.traversing.interfaces import TraversalError
from zope.app.folder import Folder
from zope.app.file import File
from zope.app.publisher.browser import BrowserView

from wikification.browser.interfaces import IWikiPage

def html_body(html) :

    output = re.compile('<body.*?>(.*?)</body>', re.DOTALL |  re.IGNORECASE).findall(html)
    if len(output) > 1 :
        print "Warning: more than one body tag."
    elif len(output) == 0 :     # hmmh, a html fragment?
        return html  
    return output[0]
    

class WikiPage(BrowserView) :
    """ A wiki page that 'wikifies' a folder with ordinary HTML documents.
    
        See wikification/README.txt for a definition of what 
        'wikification' means and doctests of the methods of this class.
        
    """
    
    editable = False
    supported = 'text/html', 'application/xhtml+xml', 'application/xml', 'text/xml'
    
    implements(IWikiPage)
    
    def __init__(self, context, request) :
        super(WikiPage, self).__init__(context, request)
        self.folder = self.getFolder()
        self.file = self.getFile()
        self.base = zapi.absoluteURL(self.folder, request)

    def wiki(self) :
        """ Show wikified version of the context. 
             
        """
        
        file = self.getFile()
        if file.contentType in self.supported :
            if self.editable :
                body = html_body(file.data)
            else :
                body = file.data
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
            return link
            
        path = link.split("/")
        try :
            zapi.traverse(self.folder, path)
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
     
      
    def createLink(self) :
        """
            Creates a wiki page at the given path.
        """
               
        path = self.request.form['path'].split(u'/')
        
        assert len(path) > 0
        
        base = self.folder
        
        
        for name in path[:-1] :
            folder = base[name] = Folder()
            base = folder
            
        file = File()
        folder[path[-1]] = file
        return file
        
    def saveText(self) :
        """ Generic store method.
            
        """
        
        text = self.request.form.get("text")        
        if self.create :
            file = self.createLink()
        else :
            file = self.file
        file.data = text    
        

        
class WikiFolderPage(WikiPage) :
    """ Wiki view for a container. """
    
    empty = File("""<html><body>Sorry, explanations later.</body></html>""", 
                        "text/html")
    
    def getFolder(self) :
        return self.context
        
    def getFile(self) :
        return self.context.get(u"index.html", self.empty)
        
        
class WikiFilePage(WikiPage) :
    """ Wiki view for a file. """
    
    def getFolder(self) :
        return self.context.__parent__
        
    def getFile(self) :
        return self.context
        
        
class EditWikiPage(WikiPage) :

    editable = True
    create = False
 
class CreateWikiPage(WikiPage) :

    editable = True
    create = True
    