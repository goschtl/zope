from zope.interface import Interface

class IRegistrations(Interface):
    """Registrations that qualify for the given lookup."""

    def byObjects():
        """Return the registrations grouped by the objects."""
