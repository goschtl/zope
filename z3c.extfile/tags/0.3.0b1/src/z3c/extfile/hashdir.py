import sha
import os
import stat
import tempfile
import shutil
from types import StringTypes, UnicodeType
import interfaces
from zope import interface
from persistent import Persistent
from zope.cachedescriptors.property import Lazy

class HashDir(Persistent):

    """a directory holding files named after their sha1 hash"""

    interface.implements(interfaces.IHashDir)
    _path = None

    def __init__(self, path=None, fallbacks=()):
        self.path = path
        self.fallbacks = map(os.path.abspath, fallbacks)

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
            os.chmod(target, 0440)
        return digest

    def digests(self):
        """returns all digests stored"""
        return os.listdir(self.var)

    def getPath(self, digest):
        if type(digest) not in StringTypes or len(digest) != 40:
            raise ValueError, repr(digest)
        if type(self.var) is UnicodeType:
            digest = unicode(digest)
        for base in [self.var] +  self.fallbacks:
            path = os.path.join(base, digest)
            if os.path.isfile(path):
                return path
        raise KeyError, digest

    def getSize(self, digest):
        return os.path.getsize(self.getPath(digest))

    def open(self, digest):
        return ReadFile(self.getPath(digest))


class ReadFile(object):

    """A lazy read file implementation"""

    interface.implements(interfaces.IReadFile)

    def __init__(self, name, bufsize=-1):
        self.name = name
        self.digest = str(os.path.split(self.name)[1])
        self.bufsize=bufsize
        self._v_len = None
        self._v_file = None

    @property
    def _file(self):
        if not self.closed:
            return self._v_file
        self._v_file = file(self.name, 'rb', self.bufsize)
        return self._v_file

    @Lazy
    def ctime(self):
        return int(os.stat(self.name)[stat.ST_CTIME])

    @Lazy
    def atime(self):
        return int(os.stat(self.name)[stat.ST_ATIME])

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
        self._pos = 0

    def write(self, s):
        self.sha.update(s)
        os.write(self.handle, s)
        self._pos += len(s)

    def commit(self):
        """returns the sha digest and saves the file"""
        os.close(self.handle)
        return self.hd.commit(self)

    def tell(self):
        """see file.tell"""
        return self._pos

    def abort(self):
        """abort the write and delete file"""
        os.close(self.handle)
        os.unlink(self.path)
