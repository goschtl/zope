import urllib

import zope.location.location
from zope import component
from zope.traversing.browser.interfaces import IAbsoluteURL
from zope.traversing.browser.absoluteurl import _safe as SAFE_URL_CHARACTERS

from zope.security.checker import NamesChecker, defineChecker
from zope.security.interfaces import IPermission

from martian.error import GrokError, GrokImportError
from martian.util import class_annotation, methods_from_class, scan_for_classes

def get_default_permission(factory):
    """Determine the default permission for a view.

    There can be only 0 or 1 default permission.
    """
    permissions = class_annotation(factory, 'grok.require', [])
    if not permissions:
        return 'zope.Public'
    if len(permissions) > 1:
        raise GrokError('grok.require was called multiple times in '
                        '%r. It may only be set once for a class.'
                        % factory, factory)

    result = permissions[0]
    return result