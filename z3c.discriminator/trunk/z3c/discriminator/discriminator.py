def discriminator(iface):
    """This method creates an interface class derived from ``iface`` that behaves
    and identifies exactly like ``iface`` except it is marked as a discriminator
    by providing ``__discriminated__``."""

    class meta(type(iface)):
        def __init__(self, name, bases=(), attrs=None, **kwargs):
            del attrs['__metaclass__']
            super(meta, self).__init__(name, bases=bases, attrs=attrs, **kwargs)
            
        def __eq__(self, other):
            if other is iface or other is self:
                return True

        def __hash__(self):
            return hash(iface)
            
    class _(iface):
        __metaclass__ = meta

    _.__discriminated__ = iface
    
    return _
