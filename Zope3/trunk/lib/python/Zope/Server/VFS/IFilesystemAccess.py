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

$Id: IFilesystemAccess.py,v 1.2 2002/06/10 23:29:37 jim Exp $
"""

from Interface import Interface

# XXX This interface should be in a more central location.

class IFilesystemAccess(Interface):
    """Provides authenticated access to a filesystem.
    """

    def authenticate(credentials):
        """Verifies filesystem access based on the presented credentials.

        Should raise Unauthorized if the user can not be authenticated.

        This method only checks general access and is not used for each
        call to open().  Rather, open() should do its own verification.
        """

    def open(credentials):
        """Returns an IReadFilesystem or IWriteFilesystem.

        Should raise Unauthorized if the user can not be authenticated.
        """
