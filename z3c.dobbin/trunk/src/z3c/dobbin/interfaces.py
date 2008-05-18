from zope import interface

class IMapped(interface.Interface):    
    __mapper__ = interface.Attribute(
        """ORM mapper.""")

class IMapper(interface.Interface):
    """An ORM mapper for a particular specification."""
