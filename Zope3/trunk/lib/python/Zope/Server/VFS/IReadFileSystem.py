##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""

$Id: IReadFileSystem.py,v 1.2 2002/06/10 23:29:37 jim Exp $
"""

from Interface import Interface

class IReadFileSystem(Interface):
    """We want to provide a complete wrapper around any and all read
       filesystem operations.

       Opening files for reading, and listing directories, should
       return a producer.

       All paths are POSIX paths, even when run on Windows,
       which mainly means that FS implementations always expect forward
       slashes, and filenames are case-sensitive.

       Note: A file system should *not* store any state!
    """

    def exists(path):
        """Test whether a path exists.
        """

    def isdir(path):
        """Test whether a path is a directory.
        """

    def isfile(path):
        """Test whether a path is a file.
        """

    def listdir(path, with_stats=0, pattern='*'):
        """Return a listing of the directory at 'path' The empty
           string indicates the current directory.  If 'with_stats' is set,
           instead return a list of (name, stat_info) tuples. All file
           names are filtered by the globbing pattern.  (See the 'glob'
           module in the Python standard library.)
        """
        return list(tuple(str, str))

    def readfile(path, mode, outstream, start=0, end=-1):
        """Outputs the file at path to a stream.
        """

    def stat(path):
        """Return the equivalent of os.stat() on the given path:

           (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime)
        """
