import zope.interface.adapter
import zope.configuration.fields

from z3c.discriminator import discriminator

_register = zope.interface.adapter.BaseAdapterRegistry.register
def register(self, required, provided, name, factory):
    """This method wraps ``factory`` so it's discriminator-aware
    if one or more ``required`` interfaces are designated as
    discriminators."""
    
    drequired = [hasattr(r, '__discriminated__') for r in required]

    if factory is None or len(drequired) == 0:
        return _register(self, required, provided, name, factory)

    def _factory(*args):
        _ = [provided for (provided, implemented) in 
             zip(args, tuple(required) + (None,) * (len(args) - len(required))) \
             if not hasattr(implemented, '__discriminated__')]

        return factory(*_)

    _register(self, required, provided, name, _factory)

# monkey-patch ``register`` method on zope.interface.adapter.BaseAdapterRegistry
zope.interface.adapter.BaseAdapterRegistry.register = register

_fromUnicode = zope.configuration.fields.GlobalObject.fromUnicode
def fromUnicode(self, u):
    """This method wraps ``fromUnicode`` so strings that begin with a
    dash are wrapped as a discriminator."""
    
    if u.startswith('-'):
        return discriminator(self.fromUnicode(u[1:]))

    return _fromUnicode(self, u)

# monkey-patch ``fromUnicode`` on zope.configuration.fields.GlobalObject.fromUnicode
zope.configuration.fields.GlobalObject.fromUnicode = fromUnicode
