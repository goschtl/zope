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

$Id: IPosixFileSystem.py,v 1.2 2002/06/10 23:29:37 jim Exp $
"""

from IWriteFileSystem import IWriteFileSystem
from IReadFileSystem import IReadFileSystem


class IPosixFileSystem(IWriteFileSystem, IReadFileSystem):
    """
    """

    def chmod(path, mode):
        """Change the access permissions of a file.
        """

    def chown(path, uid, gid):
        """Change the owner and group id of path to numeric uid and gid.
        """

    def link(src, dst):
        """Create a heard link to a file.
        """

    def mkfifo(path, mode=777):
        """Create a FIFO (a POSIX named pipe).
        """

    def symlink(src, dst):
        """Create a symbolic link at dst pointing to src.
        """

