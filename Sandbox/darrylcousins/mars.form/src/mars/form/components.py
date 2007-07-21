from z3c.pagelet.interfaces import IPagelet
from z3c.form.interfaces import IFormLayer as IZ3CFormLayer
from z3c.formui.interfaces import IDivFormLayer as IZ3CDivFormLayer
from z3c.formui.interfaces import ITableFormLayer as IZ3CTableFormLayer

from mars.layer import ILayer

class IFormLayer(ILayer, IZ3CFormLayer, IPageletBrowserLayer):
    pass

class IDivFormLayer(ILayer, IZ3CDivFormLayer, IZ3CFormLayer, IPageletBrowserLayer):
    pass

class ITableFormLayer(ILayer, IZ3CTableFormLayer, IZ3CFormLayer, IPageletBrowserLayer):
    pass


class FormView(object):
    """Vanilla view to mixin with z3c.form views"""
    zope.interface.implements(IPagelet)
