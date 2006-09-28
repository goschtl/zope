##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Import Reporter

$Id$
"""

class Reporter(object):
    """Trivial implementation of the reporter interface."""

    def request(self, importer, name, fromlist):
        """Called before the import is performed.

        `importer` is the full name of the module performing the import.

        `name` is the module name requested for the import.  This may
        be a relative module name.  It may represent a module that has
        already been loaded.

        `fromlist` is the `fromlist` argument to `__import__()`.

        This method may veto the import by raising an exception.
        """

    def found(self, importer, imported, fromlist):
        """Called after the import has been performed.

        `importer` is the full name of the module performing the import.

        `imported` is the full name of the module that was actually
        imported.

        `fromlist` is the `fromlist` argument to `__import__()`.

        This method may veto the import by raising an exception.
        """

    def exception(self, importer, name, fromlist, exc_info):
        """Called after an attempted import has failed.

        `importer` is the full name of the module performing the import.

        `name` is the module name requested for the import.  This may
        be a relative module name.  It may represent a module that has
        already been loaded.

        `fromlist` is the `fromlist` argument to `__import__()`.

        `exc_info` is the return value from sys.exc_info(), indicating
        the error that occurred.
        """
