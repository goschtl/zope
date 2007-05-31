from zope.interface import Interface

class IRegistrations(Interface):
    """Registrations that qualify for the given lookup."""

    def byObject():
        """Registrations grouped by the objects."""

    def byRegistration():
        """Registrations annotated with the objects."""
