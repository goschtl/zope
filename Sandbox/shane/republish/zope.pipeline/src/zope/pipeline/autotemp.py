##############################################################################
#
# Copyright (c) 2009 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

from cStringIO import StringIO
import tempfile

bufsize = 8192

class AutoTemporaryFile(object):
    """Initially a StringIO, but becomes a TemporaryFile if it grows big"""
    def __init__(self, threshold=bufsize):
        self._threshold = threshold
        self._f = f = StringIO()
        self._switched = False

    def read(self, count=-1):
        return self._f.read(count)

    def seek(self, pos, mode=0):
        self._f.seek(pos, mode)

    def tell(self):
        return self._f.tell()

    def close(self):
        self._f.close()

    def write(self, data):
        if not self._switched and self.tell() + len(data) >= self._threshold:
            # convert to TemporaryFile
            old = self._f
            f = tempfile.TemporaryFile()
            f.write(old.getvalue())
            f.seek(old.tell())
            self._f = f
            self._switched = True
            # delegate to the file directly
            self.read = f.read
            self.seek = f.seek
            self.tell = f.tell
            self.close = f.close
            self.write = f.write
        self._f.write(data)

    def copyfrom(self, src):
        """Fill this file with the contents of the given file"""
        while True:
            data = src.read(bufsize)
            if not data:
                break
            self.write(data)

    def copyto(self, dest):
        """Send the contents of this file to the given file"""
        while True:
            data = self.read(bufsize)
            if not data:
                break
            dest.write(data)
