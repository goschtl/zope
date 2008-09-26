from zope import interface

class IResourceLocation(interface.Interface):
    """The URL at which this resource is available. This interface
    will typically be provided by a component that adapts (context,
    request, path) and returns a string."""

