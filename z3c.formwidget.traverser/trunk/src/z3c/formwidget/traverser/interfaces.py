from zope.schema.interfaces import ISource

class IQuerySource(ISource):
    def search(traverser_string):
        """Return values that match traverser."""
