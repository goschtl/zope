##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Interfaces needed for the persistent module framework.

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.interface import Interface
from zope.schema import ASCII, BytesLine


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

