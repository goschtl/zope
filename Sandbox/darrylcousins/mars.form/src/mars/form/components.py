import zope.interface

from z3c.pagelet.interfaces import IPagelet
from z3c.layer.pagelet import IPageletBrowserLayer
from z3c.form.interfaces import IFormLayer as IZ3CFormLayer
from z3c.formui.interfaces import IDivFormLayer as IZ3CDivFormLayer
from z3c.formui.interfaces import ITableFormLayer as IZ3CTableFormLayer

from grok.interfaces import IGrokView

from mars.layer import ILayer

## layers
class IFormLayer(ILayer, IZ3CFormLayer, IPageletBrowserLayer):
    pass

class IDivFormLayer(ILayer, IZ3CDivFormLayer, IZ3CFormLayer, IPageletBrowserLayer):
    pass

class ITableFormLayer(ILayer, IZ3CTableFormLayer, IZ3CFormLayer, IPageletBrowserLayer):
    pass

## a widget template factory
class WidgetTemplateFactory(object):
    pass

class FormView(object):
    """Vanilla view to mixin with z3c.form views"""
    zope.interface.implements(IPagelet, IGrokView)
