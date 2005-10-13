from zope.app.publisher.browser import BrowserView
from zope.pagetemplate.interfaces import IPageTemplateSubclassing
from zope.app.traversing.interfaces import IPhysicallyLocatable
from zope.app.dublincore.interfaces import IZopeDublinCore 
from zope.pagetemplate.pagetemplatefile  import PageTemplateFile

__docformat__ = 'restructuredtext'

class PageInfo(object):
    """A simple page info object.
    """
    def __init__(self, context, request, template):
        self.context = context
        self.request = request
        self.response = request.response
        self.template = template 
        self.macros = {} 

    def render(self):
        return self.template.pt_render(self.__dict__) 

class WikiPageInfo(PageInfo):
    """A wiki page info object.
    """

    def getHTMLTitle(self):
        if self.title and self.site_title:
            if self.title != self.site_title:
                return '%s - %s' % (self.title, self.site_title)
        return self.title or self.site_title 

    htmlTitle = property(getHTMLTitle)

    def __init__(self, context, request):
        template = PageTemplateFile('main_template.pt')
        super(self.__class__, self).__init__(context, request, template)
        default_macros = PageTemplateFile('default_macros.pt').macros
        self.macros.update(default_macros)
        self.uris = {
            'home': '#',
            'login': '#',
            }
        self.contact_form = {
            'action_url': '#',
            }
        dc = IZopeDublinCore(self.context)
        self.dc = dc
        
        self.title = dc.Title() or 'Untitled'
        self.site = SiteInfo(self.context)
        self.site_title = self.site.title or 'No site title'
        self.html_title = self.getHTMLTitle
        self.language = dc.Language()

class SiteInfo(object):
    def __init__(self, context):
        site = IPhysicallyLocatable(context).getNearestSite()
        dc = IZopeDublinCore(site)
        self.title = dc.Title() 
        self.description = dc.Description()
