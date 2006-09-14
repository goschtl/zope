from zope import component, interface
import interfaces
from cStringIO import StringIO
from transaction.interfaces import IDataManager
from zope import thread
import transaction

_marker = object()
BLOCK_SIZE = 1024*128

_storage = thread.local()

class ExtBytesProperty(object):

    """a property which's values are stored as external files"""

    def __init__(self, name):
        self.__name = name
        

    @property
    def hd(self):
        return component.getUtility(interfaces.IHashDir)
    
    def __get__(self, inst, klass):

        if inst is None:
            return self
        digest = inst.__dict__.get(self.__name, _marker)
        if digest is _marker:
            return None

        
        if not hasattr(_storage, 'dataManager'):
            _storage.dataManager = ReadFileDataManager()
            txn = transaction.manager.get()
            if txn is not None:
                txn.join(_storage.dataManager)
        return _storage.dataManager.getFile(digest)

    def __set__(self, inst, value):
        # ignore if value is None
        if value is None:
            return
        # Handle case when value is a string
        if isinstance(value, unicode):
            value = value.encode('UTF-8')
        if isinstance(value, str):
            value = StringIO(value)
        value.seek(0)
        f = self.hd.new()
        while True:
            chunk = value.read(BLOCK_SIZE)
            if not chunk:
                digest = f.commit()
                inst.__dict__[self.__name] = digest
                break
            f.write(chunk)


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
        import logging
        logging.info('RFD.colse %r' % self.files.keys())
        for f in self.files.values():
            f.close()
        
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
