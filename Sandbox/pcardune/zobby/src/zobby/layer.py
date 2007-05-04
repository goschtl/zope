from z3c.form.interfaces import IFormLayer
from z3c.formui.interfaces import IDivFormLayer
from z3c.layer.pagelet import IPageletBrowserLayer

class IZobbyBrowserLayer(IDivFormLayer, IFormLayer, IPageletBrowserLayer):
    """Like IMinimalBrowserLayer including widget layer."""
