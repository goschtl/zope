from zope.contentprovider.interfaces import IContentProvider

class ITreeContentProvider(IContentProvider):
    def insert(tree):
        """Render and insert into the element tree."""

