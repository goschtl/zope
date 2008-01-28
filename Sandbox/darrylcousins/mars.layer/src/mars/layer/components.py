import zope.interface

from z3c.layer.pagelet import IPageletBrowserLayer
from z3c.layer.minimal import IMinimalBrowserLayer

import grok

class IMinimalLayer(grok.IGrokLayer, IMinimalBrowserLayer):
    pass

class IPageletLayer(grok.IGrokLayer, IPageletBrowserLayer):
    pass
