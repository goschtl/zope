from zope.viewlet.interfaces import IViewletManager
from zope.viewlet.viewlet import CSSViewlet
from zope.viewlet.viewlet import JavaScriptViewlet
from z3c.pagelet import browser
from z3c.formui import interfaces

import zobby.layer

class IZobbyBrowserSkin(zobby.layer.IZobbyBrowserLayer):
    """The ``Zobby`` browser skin."""
