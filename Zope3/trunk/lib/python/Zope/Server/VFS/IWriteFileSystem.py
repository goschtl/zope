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

$Id: IWriteFileSystem.py,v 1.2 2002/06/10 23:29:37 jim Exp $
"""

from Interface import Interface

class IWriteFileSystem(Interface):
    """We want to provide a complete wrapper around any and all write
       filesystem operations.

       Notes:
         - A file system should *not* store any state!
         - Most of the commands copy the functionality given in os.
    """

    def mkdir(path, mode=777):
        """Create a directory.
        """

    def remove(path):
        """Remove a file. Same as unlink.
        """

    def rmdir(path):
        """Remove a directory.
        """

    def rename(old, new):
        """Rename a file or directory.
        """

    def writefile(path, mode, instream, start=0):
        """Write data to a file.
        """

    def check_writable(path):
        """Ensures a path is writable.  Throws an IOError if not."""

