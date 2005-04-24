##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""ZCML directives for defining privileges.

$Id: $
"""
__docformat__ = "reStructuredText"
import zope.interface
import zope.schema
import zope.configuration.fields

class IdefineXpdl(zope.interface.Interface):

    file = zope.configuration.fields.Path(
        title=u"File Name",
        description=u"The name of the xpdl file to read.",
        )

    process = zope.schema.TextLine(
        title=u"Process Name",
        description=u"The name of the process to read.",
        )

    id = zope.schema.Id(
        title=u"ID",
        description=(u"The identifier to use for the process.  "
                     u"Defaults to the process name."),
        )
