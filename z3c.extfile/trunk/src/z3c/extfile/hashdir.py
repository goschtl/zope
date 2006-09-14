import sha
import os
import stat
import tempfile
import shutil
from types import StringType
import interfaces
from zope import interface
from persistent import Persistent


class HashDir(Persistent):

    """a directory holding files named after their sha1 hash"""

    interface.implements(interfaces.IHashDir)
    _path = None

    def __init__(self, path=None):
        self.path = path

    def _setPath(self, path):
        if path is None:
            return
        self._path = os.path.abspath(path)
        self.tmp = os.path.join(self.path, 'tmp')
        self.var = os.path.join(self.path, 'var')
        self._initPaths()
        
    def _getPath(self):
        return self._path

    path = property(_getPath,_setPath)

    def _initPaths(self):
        for path in [self.path,self.var,self.tmp]:
            if not os.path.exists(path):
                os.mkdir(path)
            
    def new(self):
        """returns a new filehandle"""
        handle, path = tempfile.mkstemp(prefix='dirty.',
                                        dir=self.tmp)
        return WriteFile(self, handle, path)

    def commit(self, f):
        """commit a file, this is called by the file"""
        digest = f.sha.hexdigest()
        target = os.path.join(self.var, digest)
        if os.path.exists(target):
            # we have that content so just delete the tmp file
            os.remove(f.path)
        else:
            shutil.move(f.path, target)
        return digest
        
    def digests(self):
        """returns all digests stored"""
        return os.listdir(self.var)

    def getPath(self, digest):
        if  type(digest) != StringType or len(digest) != 40:
            raise ValueError, digest
        path = os.path.join(self.var, digest)
        if not os.path.isfile(path):
            raise KeyError, digest
        return path

    def getSize(self, digest):
        return os.path.getsize(self.getPath(digest))

    def open(self, digest):
        return ReadFile(self.getPath(digest))
        

class ReadFile(object):

    """A lazy read file implementation"""

    interface.implements(interfaces.IReadFile)

    def __init__(self, name, bufsize=-1):
        self.name = name
        self.digest = os.path.split(self.name)[1]
        self.bufsize=bufsize
        self._v_len = None
        self._v_file = None

    @property
    def _file(self):
        if not self.closed:
            return self._v_file
        self._v_file = file(self.name, 'rb', self.bufsize)
        return self._v_file
    
    def __len__(self):
        if self._v_len is None:
            self._v_len = int(os.stat(self.name)[stat.ST_SIZE])
        return self._v_len

    def __repr__(self):
        return "<ReadFile named %s>" % repr(self.digest)

    @property
    def closed(self):
        """like file closed, but lazy"""
        return self._v_file is None or self._v_file.closed

    def seek(self, offset, whence=0):
        """see file.seek"""
        # we optimize when we have 0, 0 then we do not need to open
        # the file if it is closed, because on the next read we are at
        # 0
        if offset==0 and whence==0 and self.closed:
            return
        return self._file.seek(offset, whence)

    def tell(self):
        """see file.tell"""
        if self.closed:
            return 0
        return self._file.tell()

    def read(self, size=-1):
        """see file.read"""
        return self._file.read(size)

    def close(self):
        """see file.close"""
        if not self.closed:
            self._v_file.close()
        self._v_file = None
        
    def fileno(self):
        return self._file.fileno()

    def __iter__(self):
        return self._file.__iter__()



class WriteFile(object):

    interface.implements(interfaces.IWriteFile)

    def __init__(self, hd, handle, path):
        self.hd = hd
        self.handle = handle
        self.path = path
        self.sha = sha.new()

    def write(self, s):
        self.sha.update(s)
        os.write(self.handle, s)

    def commit(self):
        """returns the sha digest and saves the file"""
        os.close(self.handle)
        return self.hd.commit(self)

