##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
"""Versioned Resources Interfaces

$Id$
"""
__docformat__ = "reStructuredText"
import zope.interface
import zope.schema

class IVersionManager(zope.interface.Interface):
    """A manager for resource versions."""

    version = zope.schema.ASCIILine(
        title=u'Version',
        description=u'The versoin of the resources.',
        required=True)

class IVersionedResource(zope.interface.Interface):
    """Versioned Resource"""
