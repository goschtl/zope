
from cStringIO import StringIO

bufsize = 8192

class AutoTemporaryFile(object):
    """Initially a StringIO, but becomes a TemporaryFile if it grows big"""
    def __init__(self, threshold=bufsize):
        self._threshold = threshold
        self._f = f = StringIO()
        # delegate most methods
        for m in ('read', 'seek', 'tell', 'close'):
            setattr(self, m, getattr(f, m))

    def write(self, data):
        if self.tell() + len(data) >= self._threshold:
            # convert to TemporaryFile
            f = tempfile.TemporaryFile()
            f.write(self._f.getvalue())
            f.seek(self.tell())
            self._f = f
            # delegate all important methods
            for m in ('write', 'read', 'seek', 'tell', 'close'):
                setattr(self, m, getattr(f, m))
        self._f.write(data)

    def copyfrom(self, src):
        while True:
            data = src.read(bufsize)
            if not data:
                break
            self.write(data)

    def copyto(self, dest):
        while True:
            data = self.read(bufsize)
            if not data:
                break
            dest.write(data)
