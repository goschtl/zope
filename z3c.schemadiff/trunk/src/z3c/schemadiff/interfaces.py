from zope import interface

class IFieldDiff(interface.Interface):
    def html_diff(a, b):
        """Return an HTML diff."""

    def lines(value):
        """Return a text string lines representation."""

