from zope.interface import Interface

class IRegistrations(Interface):
    """Registrations that qualify for the given lookup."""

    def byObjects():
        """Registrations grouped by the objects."""

    def byOrder():
        """Registrations sorted by number of matched objects."""
