##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Interfaces needed by the module service.

XXX There is no module service yet; instead, the service manager
currently implements it.  This should change.

$Id$
"""

from zope.interface import Interface
from zope.schema import Bytes, ASCII, BytesLine


class IModuleManager(Interface):
    """Content object providing management support for persistent modules."""

    def execute():
        """Recompile the module source and initialize the module."""

    def getModule():
        """Return the module object that can be used from Python.

        If the module has not been initialized from the source text,
        or the source text has changed, the source will be executed by
        this method.
        """

    
    name = BytesLine(title=u"The module's name.", readonly=True)

    source = ASCII(title=u"The module's source code.")


class IModuleService(Interface):
    """Objects that can resolve dotted names to objects
    """

    def resolve(dotted_name):
        """Resolve the given dotted name to a module global variable.

        If the name ends with a trailing dot, the last name segment
        may be repeated.

        If the dotted name cannot be resolved, an ImportError is raised.
        """
