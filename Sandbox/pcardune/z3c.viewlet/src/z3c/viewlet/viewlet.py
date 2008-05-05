import os.path

from zope.viewlet.viewlet import ViewletBase
from zope.viewlet.viewlet import CSSResourceViewletBase
import zope.viewlet.viewlet
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile


class CSSViewlet(CSSResourceViewletBase, ViewletBase):

    _index = ViewPageTemplateFile(os.path.join(os.path.dirname(zope.viewlet.viewlet.__file__),
                                              'css_viewlet.pt'))
    resource = ''

    @property
    def _path(self):
        return self.resource

    def index(self):
        return self._index()
