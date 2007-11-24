import zope.interface
import zope.component.zcml
import zope.configuration.fields

from z3c.discriminator import discriminator

class DiscriminatorAwareGlobalObject(zope.configuration.fields.GlobalObject):
    def fromUnicode(self, u):
        if u.startswith('-'):
            return discriminator(self.fromUnicode(u[1:]))

        return super(DiscriminatorAwareGlobalObject, self).fromUnicode(u)
        
class IAdapterDirective(zope.component.zcml.IAdapterDirective):
    pass

IAdapterDirective['for_'].value_type = DiscriminatorAwareGlobalObject(missing_value=object())

def adapter(_context, factory, provides=None, for_=None, **kwargs):
    if len(factory) != 1:
        return zope.component.zcml.adapter(_context, factory, provides, for_, **kwargs)

    factory = factory[0]

    if for_ is None:
        for_ = zope.component.adaptedBy(factory)

        if for_ is None:
            raise TypeError("No for attribute was provided and can't "
                            "determine what the factory adapts.")

    for_ = tuple(for_)

    @zope.interface.implementer(zope.interface.implementedBy(factory))
    def _factory(*args):
        _ = [provided for (provided, implemented) in zip(args, for_)
             if not isinstance(implemented, discriminator)]
        return factory(*_)

    # unwrap discriminators
    adapts = [isinstance(a, discriminator) and a.iface or a for a in for_]
    
    zope.component.zcml.adapter(_context, [_factory], provides=provides, for_=adapts, **kwargs)
