from zope import interface
from zope import component

def discriminator(iface):
    class _(iface):
        pass

    _.__discriminated__ = iface
    _.providedBy = iface.providedBy
        
    return _
        
def provideAdapter(factory, adapts=None, provides=None, name=''):
    def _factory(*args):
        _ = [provided for (provided, implemented) in zip(args, adapts)
             if not hasattr(implemented, '__discriminated__')]
        return factory(*_)

    # unwrap discriminators
    _adapts = [getattr(a, '__discriminated__', a) for a in adapts]

    component.provideAdapter(_factory, _adapts, provides, name)
