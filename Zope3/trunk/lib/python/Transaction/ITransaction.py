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
try:
    from Interface import Interface
except ImportError:
    class Interface: pass

class ITransaction(Interface):
    """Transaction objects

    Application code typically gets these by calling
    get_transaction().
    """

    def abort():
        """Abort the current transaction."""

    def begin():
        """Begin a transaction."""

    def commit():
        """Commit a transaction."""

    def join(resource):
        """Join a resource manager to the current transaction."""

    def status():
        """Return status of the current transaction."""
