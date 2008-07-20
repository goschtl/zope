import urllib

from zope import component
from zope.traversing.browser.interfaces import IAbsoluteURL
from zope.traversing.browser.absoluteurl import _safe as SAFE_URL_CHARACTERS
from zope.security.checker import NamesChecker, defineChecker
from zope.security.interfaces import IPermission

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

def make_checker(factory, view_factory, permission, method_names=None):
    """Make a checker for a view_factory associated with factory.

    These could be one and the same for normal views, or different
    in case we make method-based views such as for JSON and XMLRPC.
    """
    if method_names is None:
        method_names = ['__call__']
    if permission is not None:
        check_permission(factory, permission)
    if permission is None or permission == 'zope.Public':
        checker = NamesChecker(method_names)
    else:
        checker = NamesChecker(method_names, permission)
    defineChecker(view_factory, checker)

def check_permission(factory, permission):
    """Check whether a permission is defined.

    If not, raise error for factory.
    """
    if component.queryUtility(IPermission,
                              name=permission) is None:
        raise GrokError('Undefined permission %r in %r. Use '
                        'grok.Permission first.'
                        % (permission, factory), factory)

