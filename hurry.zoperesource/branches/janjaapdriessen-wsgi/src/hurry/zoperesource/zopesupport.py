# zope integration for hurry.resource
from zope.browserresource import directory
from zope.component import adapts, adapter, getMultiAdapter
from zope.interface import alsoProvides, implements
from zope.publisher.interfaces import IEndRequestEvent, IRequest
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.site.hooks import getSite
from zope.traversing.browser.interfaces import IAbsoluteURL
import zope.browserresource.resource
import zope.security.management

from hurry.resource import NeededInclusions
from hurry.resource.wsgi import NEEDED

from hurry.zoperesource.interfaces import IHurryResource

class NoRequestError(Exception):
    pass


def getRequest():
    try:
        i = zope.security.management.getInteraction()  # raises NoInteraction
    except zope.security.interfaces.NoInteraction:
        raise NoRequestError()

    for p in i.participations:
        if IRequest.providedBy(p):
            return p

    raise NoRequestError()


class Plugin(object):
    """Zope implementation of plugin.

    This implementation provides access to the WSGI environment, in which
    we place a NeededInclusions object upon needing resources.
    """
    def get_current_needed_inclusions(self):
        request = getRequest()
        # Find the NeededInclusions object in the WSGI environment; If
        # none can be found, create a new one and add it to the
        # environment.  Unfortunately we don't have easy access to the
        # WSGI environment, so we have to use request._orig_env.
        return request._orig_env.setdefault(NEEDED, NeededInclusions())

@adapter(IEndRequestEvent)
def set_base_url_on_needed_inclusions(event):
    request = event.request
    # Unfortunately we don't have easy access to the WSGI environment,
    # so we have to use request._orig_env.
    needed = request._orig_env.get(NEEDED)
    if needed is not None and needed.base_url is None:
        # Only set the base_url if resources have been needed during
        # this request.
        site_url = str(getMultiAdapter((getSite(), request), IAbsoluteURL))
        needed.base_url = '%s/@@' % site_url

# Custom DirectoryResource(Factory) implementations that allow to
# inject the library object that the IAbsoluteURL adapter can use.

def hurrify(resource, library):
    alsoProvides(resource, IHurryResource)
    resource.library = library
    return resource

class DirectoryResource(directory.DirectoryResource):

    implements(IHurryResource)

    def directory_factory(self, path, checker, name):
        directory_resource = DirectoryResourceFactory(path, checker, name)
        return hurrify(directory_resource, self.library)
        
    def get(self, name, *args, **kw):
        resource = super(DirectoryResource, self).get(name, *args, **kw)
        return hurrify(resource, self.library)

class DirectoryResourceFactory(directory.DirectoryResourceFactory):

    factoryClass = DirectoryResource

    def __call__(self, request):
        resource = super(DirectoryResourceFactory, self).__call__(request)
        return hurrify(resource, self.library)

# "Top-level" directory resource factory, that allows us to inject the
# library object. This, with the custom DirectoryResource(Factory)
# implementation then is used to inject the libary object as an
# attribute on all the subsequent resources. The IAbsoluteURL adapter
# for IHurryResource is thus able to compute library URLs.
class HurryDirectoryResourceFactory(DirectoryResourceFactory):

    def __init__(self, library, checker):
        super(HurryDirectoryResourceFactory, self).__init__(
            library.path, checker, library.name)
        self.library = library

# Adapter for constructing URLs from page templates using
# `context/++resource++foo` that may point to the hurry.resource
# publisher.
class AbsoluteURL(zope.browserresource.resource.AbsoluteURL):

    adapts(IHurryResource, IBrowserRequest)

    def __str__(self):
        site_url = str(
            getMultiAdapter((getSite(), self.request), IAbsoluteURL))
        return '%s/@@/%s/%s' % (
            site_url, self.context.library.signature(), self.context.__name__)
