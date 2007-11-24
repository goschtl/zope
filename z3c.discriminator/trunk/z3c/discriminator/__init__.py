from zope import interface
from zope import component

class discriminator(object):
    interface.implements(interface.interfaces.ISpecification,
                         interface.interfaces.IInterface)
    
    def __init__(self, iface):
        self.iface = iface
        self.__name__ = iface.__name__
        interface.alsoProvides(self, iface)
        
def provideAdapter(factory, adapts=None, provides=None, name=''):
    def _factory(*args):
        _ = [provided for (provided, implemented) in zip(args, adapts)
             if not isinstance(implemented, discriminator)]
        return factory(*_)

    # unwrap discriminators
    _adapts = [isinstance(a, discriminator) and a.iface or a for a in adapts]

    component.provideAdapter(_factory, _adapts, provides, name)
