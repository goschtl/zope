import urllib

from zope import component
from zope.traversing.browser.interfaces import IAbsoluteURL
from zope.traversing.browser.absoluteurl import _safe as SAFE_URL_CHARACTERS
from zope.security.interfaces import IPermission
from zope.app.security.protectclass import protectName

from martian.error import GrokError


def url(request, obj, name=None, data={}):
    url = component.getMultiAdapter((obj, request), IAbsoluteURL)()
    if name is not None:
        url += '/' + urllib.quote(name.encode('utf-8'), SAFE_URL_CHARACTERS)
    if data:
        for k, v in data.items():
            if isinstance(v, unicode):
                data[k] = v.encode('utf-8')
            if isinstance(v, (list, set, tuple)):
                data[k] = [isinstance(item, unicode) and item.encode('utf-8')
                or item for item in v]
        url += '?' + urllib.urlencode(data, doseq=True)
    return url


def default_view_name(factory, module=None, **data):
    return factory.__name__.lower()


def default_fallback_to_name(factory, module, name, **data):
    return name

def protect_name(class_, name, permission=None):
    # Define an attribute checker using zope.app.security's
    # protectName that defaults to the 'zope.Public' permission when
    # it's not been given and makes sure the permission has actually
    # been defined when it has.
    if permission is None:
        permission = 'zope.Public'
    else:
        check_permission(class_, permission)
    protectName(class_, name, permission)

def check_permission(factory, permission):
    """Check whether a permission is defined.

    If not, raise error for factory.
    """
    if component.queryUtility(IPermission,
                              name=permission) is None:
        raise GrokError('Undefined permission %r in %r. Use '
                        'grok.Permission first.'
                        % (permission, factory), factory)
