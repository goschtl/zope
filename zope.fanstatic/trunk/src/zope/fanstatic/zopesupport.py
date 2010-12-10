from zope.interface import implements
from zope.component import adapter
from zope.publisher.interfaces import IEndRequestEvent
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.traversing.browser.interfaces import IAbsoluteURL
from zope.traversing.interfaces import ITraversable

import fanstatic

@adapter(IEndRequestEvent)
def set_base_url_on_needed_inclusions(event):
    needed = fanstatic.get_needed()
    if needed.base_url is None:
        needed.base_url = absoluteURL(None, event.request)

class ZopeFanstaticResource(object):

    # Hack to get ++resource++foo/bar/baz.jpg paths working in Zope
    # Pagetemplates. Note that ++resource+foo/bar/baz.jpg URLs will
    # not work with this hack!

    implements(ITraversable, IAbsoluteURL)

    def __init__(self, request, library, name=''):
        self.request = request
        self.library = library
        self.name = name

    def traverse(self, name, furtherPath):
        name = '%s/%s' % (self.name, name)
        # XXX check whether the request resource actually exists and
        # warn if not.
        return ZopeFanstaticResource(self.request, self.library, name=name)

    def __str__(self):
        needed = fanstatic.get_needed()
        if needed.base_url is None:
            needed.base_url = absoluteURL(None, self.request)
        return needed.library_url(self.library) + self.name
