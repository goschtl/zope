from zope import interface
from zope.formlib import form
from zope.dublincore.interfaces import IWriteZopeDublinCore
from zope.dublincore.interfaces import IZopeDublinCore
from z3c.reference.demo.interfaces import (IDemoFolder, IDemoImage)

from zope.traversing.browser.absoluteurl import absoluteURL
from zope.traversing.api import getPath

from zope import component
from zope.app.intid.interfaces import IIntIds
from zc import resourcelibrary

class DemoFolderEdit(form.EditForm):
    form_fields = form.Fields(IDemoFolder)


class DemoImageEdit(form.EditForm):
    form_fields = form.Fields(IDemoImage)


class AddRef(object):
    
    def items(self):
        intIds = component.getUtility(IIntIds)
        for o in self.context.values():
            if str(o.__class__) == u"<class 'zope.app.intid.IntIds'>":
                continue
            yield dict(
                name = o.__name__,
                uid=intIds.getId(o))

    @property
    def url(self):
        return absoluteURL(self.context, self.request)


class Test(object):
    def test(self):
        intIds = component.getUtility(IIntIds)
        print self.context
        return intIds.getId(self.context)

            
class DemoPicker(object):
    
    def elements(self):
        return self.context.values()

    @property
    def url(self):
        return absoluteURL(self.context, self.request)


class Meta(object):
    """Update dc title."""

    def edit(self):
        request = self.request
        dc = IZopeDublinCore(self.context)
        
        if 'dctitle' in request:
            dc.title = unicode(request['dctitle'])
        
        return {
            'dctitle': dc.title,
            }

    @property
    def url(self):
        return absoluteURL(self.context, self.request)
