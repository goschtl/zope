from zope.interface import implements
from zope.dublincore.interfaces import IZopeDublinCore
from zope.app.container.contained import Contained
from persistent import Persistent
from z3c.weblog.interfaces import IEntry, IEntryContained, IDCEntry

class Entry(Persistent, Contained):
    """A Weblog Entry

    >>> e = Entry()
    >>>
    """

    implements(IEntry, IEntryContained)

    # See weblog.interfaces.IEntry
    content = None


class DCEntry(object):
    """Weblog Entry with Dublin Core support
    
    >>> e = DCEntry(Entry())
    >>>
    """
    
    implements(IDCEntry)
    __used_for__ = IEntry

    def __init__(self, entry):
        self._entry = entry

    def getTitle(self):
        return IZopeDublinCore(self._entry).title
    
    def setTitle(self, title):
        IZopeDublinCore(self._entry).title = title

    title = property(getTitle, setTitle, doc="Weblog Entry title")

    def getDescription(self):
        return IZopeDublinCore(self._entry).description
    
    def setDescription(self, description):
        IZopeDublinCore(self._entry).description = description

    description = property(getDescription, setDescription,
                           doc="Description of the Weblog Entry")
    
    def getContent(self):
        return self._entry.content
    
    def setContent(self, content):
        self._entry.content = content

    content = property(getContent, setContent,
                       doc="Content of the Weblog Entry")
    


