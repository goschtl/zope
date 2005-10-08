from zope.app.publisher.browser import BrowserView
from zope.pagetemplate.interfaces import IPageTemplateSubclassing
from zope.app.traversing.interfaces import IPhysicallyLocatable
from zope.app.dublincore.interfaces import IZopeDublinCore 

__docformat__ = 'restructuredtext'

class PageInfo(object):
    """A simple page info object.
    """
    def __init__(self, context, request, template):
        self.context = context
        self.request = request
        self.response = request.response
        self.template = template 
        self.macros = IPageTemplateSubclassing(template).macros

    def render(self):
        return self.template.pt_render(self.__dict__) 

class HTMLPageInfo(PageInfo):
    pass
    
class WikiPageInfo(PageInfo):
    """A wiki page info object.
    """

    def getHTMLTitle(self):
        if self.title and self.site_title:
            if self.title != self.site_title:
                return '%s - %s' % (self.title, self.site_title)
        return self.title or self.site_title 

    def __init__(self, *args):
        super(self.__class__, self).__init__(*args)
        dc = IZopeDublinCore(self.context)
        self.dc = dc
       
        self.title = dc.title # dc.Title()
        self.site = SiteInfo(self.context)
        self.site_title = self.site.title
        self.html_title = self.getHTMLTitle

class SiteInfo(object):
    def __init__(self, context):
        site = IPhysicallyLocatable(context).getNearestSite()
        dc = IZopeDublinCore(site)
        self.title = dc.Title() 
        self.description = dc.Description()

def view():
    page = HTMLPage(title='foo')
    return page.render()

