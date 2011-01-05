from zope.interface import implements
from zope.component import adapter
from zope.publisher.interfaces import IEndRequestEvent
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.traversing.browser.interfaces import IAbsoluteURL
from zope.traversing.interfaces import ITraversable

import fanstatic

from zope.fanstatic.interfaces import IZopeFanstaticResource

@adapter(IEndRequestEvent)
def set_base_url_on_needed_inclusions(event):
    needed = fanstatic.get_needed()
    if needed.base_url is None:
        needed.base_url = absoluteURL(None, event.request)

_sentinel = object()

class ZopeFanstaticResource(object):

    # Hack to get ++resource++foo/bar/baz.jpg *paths* working in Zope
    # Pagetemplates. Note that ++resource+foo/bar/baz.jpg *URLs* will
    # not work with this hack!
    #
    # The ZopeFanstaticResource class also implements an __getitem__()
    # / get() interface, to support rendering URLs to resources from
    # code.

    implements(IZopeFanstaticResource, ITraversable, IAbsoluteURL)

    def __init__(self, request, library, name=''):
        self.request = request
        self.library = library
        self.name = name

    def get(self, name, default=_sentinel):
        # XXX return default if given, or NotFound (or something) when
        # not, in case name is not resolved to an actual resource.
        name = '%s/%s' % (self.name, name)
        return ZopeFanstaticResource(self.request, self.library, name=name)

    def traverse(self, name, furtherPath):
        return self.get(name)

    def __getitem__(self, name):
        resource = self.get(name, None)
        if resource is None:
            raise KeyErro(name)
        return resource

    def __str__(self):
        needed = fanstatic.get_needed()
        if needed.base_url is None:
            needed.base_url = absoluteURL(None, self.request)
        return needed.library_url(self.library) + self.name

    __call__ = __str__
