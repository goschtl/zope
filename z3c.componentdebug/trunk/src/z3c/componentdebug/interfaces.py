from zope.interface import Interface

class IRegistrations(Interface):
    """Registrations that qualify for the given lookup."""

    def byObject():
        """Registrations grouped by the objects."""
