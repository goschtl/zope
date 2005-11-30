from zope.interface import Interface

class IZope2HandledException(Interface):
    """This exception must be handled by zope 2.

    We don't even try to look up an exception view for it.
    """

class IZope2NotFound(Interface):
    pass

