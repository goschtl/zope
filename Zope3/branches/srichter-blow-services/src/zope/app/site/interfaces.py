from zope.app.component.interfaces import registration

class ILocalService(registration.IRegisterable):
    """A local service isn't a local service if it doesn't implement this.

    The contract of a local service includes collaboration with
    services above it.  A local service should also implement
    IRegisterable (which implies that it is adaptable to
    IRegistered).  Implementing ILocalService implies this.
    """
class ISimpleService(ILocalService):
    """Most local services should implement this instead of ILocalService.

    It implies a specific way of implementing IRegisterable,
    by subclassing IAttributeRegisterable.
    """
