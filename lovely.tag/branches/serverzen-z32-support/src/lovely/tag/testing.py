import zope.interface
import zope.component
import zope.app.keyreference.interfaces

class SimpleKeyReference(object):
    """An IReference for all objects. This implementation is *not* ZODB safe.
    """
    zope.component.adapts(zope.interface.Interface)
    zope.interface.implements(zope.app.keyreference.interfaces.IKeyReference)

    key_type_id = 'zope.app.keyreference.simple'

    def __init__(self, object):
        self.object = object

    def __call__(self):
        return self.object

    def __hash__(self):
        return hash(self.object)

    def __cmp__(self, other):
        if self.key_type_id == other.key_type_id:
            return cmp(hash(self.object), hash(other))

        return cmp(self.key_type_id, other.key_type_id)
