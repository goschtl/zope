import threading
from zope import interface
from zope import component
from transaction.interfaces import IDataManager
import interfaces
import transaction

_storage = threading.local()

def getFile(digest):
    if not hasattr(_storage, 'dataManager'):
        _storage.dataManager = ReadFileDataManager()
        txn = transaction.manager.get()
        if txn is not None:
            txn.join(_storage.dataManager)
    return _storage.dataManager.getFile(digest)


class ReadFileDataManager(object):

    """Takes care of closing open files"""

    interface.implements(IDataManager)

    def __init__(self):
        self.files = {}

    @property
    def hd(self):
        return component.getUtility(interfaces.IHashDir)

    def getFile(self, digest):
        if digest in self.files:
            return self.files[digest]
        self.files[digest] = self.hd.open(digest)
        return self.files[digest]

    def _close(self):
        for f in self.files.values():
            f.close()
        self.files = {}
        try:
            del _storage.dataManager
        except AttributeError:
            pass

    def abort(self, trans):
        self._close()

    def tpc_begin(self, trans):
        pass

    def commit(self, trans):
        self._close()

    def tpc_vote(self, trans):
        pass

    def tpc_finish(self, trans):
        self._close()

    def tpc_abort(self, trans):
        self._close()

    def sortKey(self):
        return str(id(self))
