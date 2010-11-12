# zope integration for hurry.resource
from zope import component
from zope.component.hooks import getSite
import zope.security.management
from zope.publisher.interfaces import IRequest
from zope.traversing.browser.interfaces import IAbsoluteURL
from grokcore.component import subscribe
from zope.publisher.interfaces import IEndRequestEvent

from hurry.resource import NeededInclusions
from hurry.resource.wsgi import KEY

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

        # Find the NeededInclusions object in the WSGI environment;
        # If none can be found, create a new one and add it to the
        # environment.
        # Unfortunately we don't have easy access to the WSGI environment,
        # so we have to use request._orig_env.
        return request._orig_env.setdefault(KEY, NeededInclusions())

@subscribe(IEndRequestEvent)
def set_base_url_on_needed_inclusions(event):
    request = event.request
    needed = request._orig_env.get(KEY)
    # We only set the base_url if resources have been needed during this
    # request and the base_url has not been set yet.
    if needed is not None and needed.base_url is None:
        needed.base_url = str(component.getMultiAdapter(
            (getSite(), request), IAbsoluteURL)) + '/@@/'
