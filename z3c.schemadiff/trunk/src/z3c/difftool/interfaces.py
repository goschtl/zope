from zope import interface

class IFieldDiff(interface.Interface):
    def lines(value):
        """Return a text string lines representation."""
