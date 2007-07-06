from zope.publisher.interfaces.browser import IBrowserRequest
import zope.interface
from z3c.layer.pagelet import IPageletBrowserLayer
from z3c.layer.minimal import IMinimalBrowserLayer
from z3c.form.interfaces import IFormLayer as IZ3CFormLayer
from z3c.formui.interfaces import IDivFormLayer as IZ3CDivFormLayer
from z3c.formui.interfaces import ITableFormLayer as IZ3CTableFormLayer

class ILayer(zope.interface.Interface):
    pass

class IMinimalLayer(ILayer, IMinimalBrowserLayer):
    pass

class IPageletLayer(ILayer, IPageletBrowserLayer):
    pass

class IFormLayer(ILayer, IZ3CFormLayer, IPageletBrowserLayer):
    pass

class IDivFormLayer(ILayer, IZ3CDivFormLayer, IZ3CFormLayer, IPageletBrowserLayer):
    pass

class ITableFormLayer(ILayer, IZ3CTableFormLayer, IZ3CFormLayer, IPageletBrowserLayer):
    pass

class Skin(object):
    pass


