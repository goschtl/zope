"""Infos about BTrees.
"""
import grokcore.component as grok
from BTrees.Interfaces import IBTree
from BTrees.OOBTree import OOBTree
from zope.proxy import removeAllProxies
from zope.site.folder import Folder
from grokui.zodbbrowser.interfaces import IBTreeInfo
from grokui.zodbbrowser.objectinfo import ObjectInfo

class BTreeInfo(ObjectInfo):
    """Infos about Btree instances.
    """
    grok.context(OOBTree)
    grok.implements(IBTreeInfo)
    grok.provides(IBTreeInfo)

    obj = None
    def __init__(self, context):
        super(BTreeInfo, self).__init__(context)
        self.obj = removeAllProxies(context)
        self._name = None
        self._parent_oid = None

    @property
    def name(self):
        """Get name of wrapped obj.
        """
        if self._name is not None:
            return self._name
        return getattr(self.obj, '__name__', u'???')

class FolderInfo(BTreeInfo):
    """Infos about folders.
    """
    grok.context(Folder)
