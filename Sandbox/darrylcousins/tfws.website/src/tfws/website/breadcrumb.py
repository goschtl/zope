import zope.interface

from z3c.breadcrumb.browser import Breadcrumbs as Breadcrumbs_
from z3c.breadcrumb.interfaces import IBreadcrumbs

import grok

class Breadcrumbs(grok.MultiAdapter, Breadcrumbs_):
    """Breadcrumbs implementation using IBreadcrumb adapters."""
    grok.name('breadcrumbs')
    grok.context(zope.interface.Interface)
    grok.provides(IBreadcrumbs)

