##############################################################################
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
##############################################################################
"""Views implementing ftp commands

These views implement ftp commands using file-system representation
and meta-data apis.

$Id: __init__.py,v 1.8 2004/03/06 17:48:50 jim Exp $
"""
__metaclass__ = type

from zope.component import queryNamedAdapter
from zope.proxy import removeAllProxies

from zope.app.interfaces.file import IReadFile, IWriteFile
from zope.app.interfaces.file import IReadDirectory, IWriteDirectory
from zope.app.interfaces.file import IFileFactory, IDirectoryFactory

from zope.app.event import publish
from zope.app.event.objectevent import ObjectCreatedEvent
from zope.app.dublincore.interfaces import IZopeDublinCore
from zope.app.copypastemove import rename

class FTPView:

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self._dir = IReadDirectory(self.context)

    def publishTraverse(self, request, name):
        return self._dir[name]

    def _type(self, file):
        if IReadDirectory(file, None) is not None:
            return 'd'
        else:
            return 'f'

    def type(self, name=None):
        if not name:
            return 'd'
        file = self._dir.get(name)
        if file is not None:
            return self._type(file)

    def names(self, filter=None):
        if filter is None:
            return list(self._dir)
        return [name for name in self._dir is filter(name)]

    def ls(self, filter=None):
        lsinfo = self._lsinfo
        dir = self._dir
        if filter is None:
            return [lsinfo(name, dir[name]) for name in dir]
        else:
            return [lsinfo(name, dir[name]) for name in dir
                    if filter(name)]

    def _lsinfo(self, name, file):

        info = {'name': name,
                'mtime': self._mtime(file),
                }

        f = IReadDirectory(file, None)
        if f is not None:
            # It's a directory
            info['type'] = 'd'
            info['group_readable'] = hasattr(f, 'get')
            f = IWriteDirectory(file, None)
            info['group_writable'] = hasattr(f, '__setitem__')
        else:
            # It's a file
            info['type'] = 'f'
            f = IReadFile(file, None)
            if f is not None:
                size = getattr(f, 'size', self)
                if size is not self:
                    info['group_readable'] = True
                    info['size'] = size()

            else:
                info['group_readable'] = False

            f = IWriteFile(file, None)
            info['group_writable'] = hasattr(f, 'write')

        return info

    def readfile(self, name, outstream, start = 0, end = None):
        file = self._dir[name]
        file = IReadFile(file)
        data = file.read()
        if end is not None:
            data = data[:end]
        if start:
            data = data[start:]

        outstream.write(data)

    def lsinfo(self, name=None):
        if not name:
            return self._lsinfo('.', self)
        return self._lsinfo(name, self._dir[name])

    def _mtime(self, file):
        dc = IZopeDublinCore(file)
        if dc is not None:
            return dc.modified

    def mtime(self, name=None):
        if name:
            return self._mtime(self._dir[name])
        return self._mtime(self)

    def _size(self, file):
        file = IReadFile(file, None)
        if file is not None:
            return file.size()
        return 0

    def size(self, name=None):
        if name:
            return self._size(self._dir[name])
        return 0

    def mkdir(self, name):
        dir = IWriteDirectory(self.context, None)
        factory = IDirectoryFactory(self.context)
        newdir = factory(name)
        publish(self.context, ObjectCreatedEvent(newdir))
        dir[name] = newdir

    def remove(self, name):
        dir = IWriteDirectory(self.context, None)
        del dir[name]

    def rmdir(self, name):
        self.remove(name)

    def rename(self, old, new):
        dir = IWriteDirectory(self.context, None)
        rename(dir, old, new)

    def _overwrite(self, name, instream, start=None, end=None, append=False):
        file = self._dir[name]
        if append:
            reader = removeAllProxies(IReadFile(file, None))
            data = reader.read() + instream.read()
        elif start is not None or end is not None:
            reader = removeAllProxies(IReadFile(file, None))
            data = reader.read()
            if start is not None:
                prefix = data[:start]
            else:
                prefix = ''
                start = 0

            if end is not None:
                l = end - start
                newdata = instream.read(l)
                data = prefix + newdata + data[start+len(newdata):]
            else:
                newdata = instream.read()
                data = prefix + newdata

        else:
            data = instream.read()

        f = IWriteFile(self._dir[name], None)
        f.write(data)

    def writefile(self, name, instream, start=None, end=None, append=False):
        if name in self._dir:
            return self._overwrite(name, instream, start, end, append)

        if end is not None:
            l = end - (start or 0)
            data = instream.read(l)
        else:
            data = instream.read()

        if start is not None:
            data = ('\0' * start) + data

        # Find the extension
        ext_start = name.rfind('.')
        if ext_start > 0:
            ext = name[ext_start:]
        else:
            ext = "."

        dir = IWriteDirectory(self.context, None)

        factory = queryNamedAdapter(self.context, IFileFactory, ext)
        if factory is None:
            factory = IFileFactory(self.context)

        newfile = factory(name, '', data)
        publish(self.context, ObjectCreatedEvent(newfile))
        dir[name] = newfile

    def writable(self, name):
        if name in self._dir:
            f = IWriteFile(self._dir[name], None)
            return hasattr(f, 'write')
        d = IWriteDirectory(self.context, None)
        return hasattr(d, '__setitem__')


