from zope.proxy import ProxyBase, getProxiedObject
from ZPublisher.Iterators import IStreamIterator

class blobfilestream_iterator(ProxyBase):
    """A filestream iterator that supports range responses."""

    __implements__ = (IStreamIterator,)

    def __new__(self, file, streamsize=1<<16):
        return ProxyBase.__new__(self, file)

    def __init__(self, file, streamsize=1<<16):
        ProxyBase.__init__(self, file)
        self.streamsize = streamsize

    def next(self):
        data = self.read(self.streamsize)
        if not data:
            raise StopIteration
        return data

