from zope.interface import implements
from zope.dublincore.interfaces import IZopeDublinCore
from zope.app.container.btree import BTreeContainer

from z3c.weblog.interfaces import IWeblog, IDCWeblog, IEntry, IDCEntry

class Weblog(BTreeContainer):
    """A Weblog using BTreeContainer
    """

    implements(IWeblog)
    

class DCWeblog(object):

    implements(IDCWeblog)
    __used_for__ = IWeblog

    def __init__(self, weblog):
        self._weblog = weblog

    def getTitle(self):
        """getTitle"""
        return IZopeDublinCore(self._weblog).title

    def setTitle(self, title):
        """setTitle"""
        IZopeDublinCore(self._weblog).title = title

    title = property(getTitle, setTitle, doc="The Weblog's title")

    def getDescription(self):
        """getDesc"""
        return IZopeDublinCore(self._weblog).description
    
    def setDescription(self, description):
        """getDesc"""
        IZopeDublinCore(self._weblog).description = description

    description = property(getDescription, setDescription,
                           doc="Description of the Weblog")
    
