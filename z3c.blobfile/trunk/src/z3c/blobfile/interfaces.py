##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""File interfaces

$Id$
"""
__docformat__ = 'restructuredtext'

import zope.interface

import zope.app.file.interfaces

class IConsumable(zope.interface.Interface):
    """Support for Blob `consumeFile`
    """

    def __call__(data):
        """Return a consumable file name or None

        If the data doesn't represent a consumable file None is returned
        """

class IOpenable(zope.interface.Interface):
    """Openable File
    """

    def open(mode):
        """Open file and return the file descriptor
        """

class AmbiguousConsumables(Exception):
    """More than one consumable
    """
