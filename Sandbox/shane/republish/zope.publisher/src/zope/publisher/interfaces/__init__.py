

from zope.deferredimport import deprecatedFrom as _deprecatedFrom

from zope.publisher.interfaces.base import *
from zope.publisher.interfaces.exceptions import *
from zope.publisher.interfaces.http import IRedirect
from zope.publisher.interfaces.http import Redirect

__all__ = tuple(name for name in globals() if not name.startswith('_'))

_deprecatedFrom("Moved to zope.complextraversal.interfaces",
    "zope.complextraversal.interfaces",
    "IPublishTraverse")
