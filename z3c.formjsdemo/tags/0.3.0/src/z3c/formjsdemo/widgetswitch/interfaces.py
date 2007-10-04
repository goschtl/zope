##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""Widget Switch Interfaces

$Id$
"""
__docformat__="restructuredtext"
import zope.interface
import zope.schema

class IContact(zope.interface.Interface):
    """A simple contact."""

    name = zope.schema.TextLine(
        title=u"Name",
        description=u"The name.",
        required=True)

    street = zope.schema.TextLine(
        title=u"Street",
        description=u"The street name and house number.",
        required=True)

    city = zope.schema.TextLine(
        title=u"City",
        description=u"The city.",
        required=True)

    zip = zope.schema.TextLine(
        title=u"ZIP",
        description=u"The Zip code.",
        required=True)

    phone = zope.schema.TextLine(
        title=u"Phone",
        description=u"The phone.",
        required=False)

    age = zope.schema.Int(
        title=u"Age",
        description=u"The age.",
        required=False)
