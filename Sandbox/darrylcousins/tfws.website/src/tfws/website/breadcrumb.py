import zope.interface
import zope.component
import zope.traversing
from zope.app.component.interfaces import ISite
from zope.publisher.interfaces import INotFound

from z3c.breadcrumb.browser import Breadcrumbs as Breadcrumbs_
from z3c.breadcrumb.interfaces import IBreadcrumbs, IBreadcrumb

import grok

from tfws.website import interfaces

class Breadcrumbs(grok.MultiAdapter, Breadcrumbs_):
    """Breadcrumbs implementation using IBreadcrumb adapters."""
    grok.name('breadcrumbs')
    grok.context(zope.interface.Interface)
    grok.provides(IBreadcrumbs)

    @property
    def crumbs(self):
        objects = []
        for obj in ( [self.context] +
                     list(zope.traversing.api.getParents(self.context)) ):
            if INotFound.providedBy(obj):
                obj = obj.getObject()
            objects.append(obj)
            if ISite.providedBy(obj):
                break
        objects.reverse()
        for object in objects:
            info = zope.component.getMultiAdapter((object, self.request),
                                        IBreadcrumb)
            yield {'name': info.name,
                   'url': info.url,
                   'activeURL': info.activeURL}

