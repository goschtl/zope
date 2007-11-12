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


class IStorage(zope.interface.Interface):
    """Store file data
    """

    def store(data, blob):
        """Store the data into the blob

	Raises NonStorable if data is not storable.
        """


class IOpenable(zope.interface.Interface):
    """Openable file
    """

    def open(mode):
        """Open file and return the file descriptor
        """


class NotStorable(Exception):
    """Data is not storable
    """

