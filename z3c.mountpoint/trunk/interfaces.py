##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
"""A simple multi-database mount-point implementation

$Id$
"""
__docformat__ = "reStructuredText"
import zope.interface
import zope.schema


class IMountPoint(zope.interface.Interface):
    """A simple mount point."""

    connectionName = zope.schema.Choice(
        title=u'Conenction Name',
        vocabulary='ZODB Connection Names',
        required=True)

    objectPath = zope.schema.TextLine(
        title=u'Object Path',
        default=u'/',
        required=True)

    objectName = zope.schema.TextLine(
        title=u'Object Name',
        description=u'The name under which the object will be known '
                    u'when traversing from the mount point.',
        default=u'object',
        required=True)

    object = zope.schema.Field(
        title=u'Foreign object')

    def update():
        """Update the mounted object."""


class IRemoteLocationProxy(zope.interface.Interface):
    """Remote Location Proxy

    When an object from a different object database is used, the directly
    specified parent is not the correct one anymore. The parent should point
    to the local mount point and subsequent objects in the path to the
    location proxied parent.
    """
