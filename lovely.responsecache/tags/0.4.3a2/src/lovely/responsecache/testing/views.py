from zope.contentprovider.interfaces import IContentProvider, UpdateNotCalled
from zope.contentprovider.interfaces import BeforeUpdateEvent
from zope.event import notify
from zope import interface
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from lovely.responsecache import view

class HourCacheSettings(view.ResponseCacheSettings):
    lifetime=3600


class TestPage(object):
    interface.implements(IContentProvider)

    template = ViewPageTemplateFile('test.pt')
    __updated = False

    def update(self):
        # make sure that our update is called before each render
        self.__updated = True
        self.x = 1
        
    def render(self):
        if not self.__updated:
            raise UpdateNotCalled
        return self.template()
    
    def __call__(self):
        notify(BeforeUpdateEvent(self, self.request))
        self.update()
        return self.render()
