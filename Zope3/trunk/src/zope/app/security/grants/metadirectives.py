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
"""Grant Directive Schema

$Id: metadirectives.py,v 1.1 2003/08/02 20:05:36 srichter Exp $
"""
from zope.interface import Interface
from zope.schema import BytesLine, Id 

class IGrantDirective(Interface):
    """Grant Permissions to roles and principals and roles to principals."""

    principal = BytesLine(
        title=u"Principal",
        description=u"Specifies the Principal to be mapped.",
        required=False)

    permission = Id(
        title=u"Permission",
        description=u"Specifies the Permission to be mapped.",
        required=False)

    role = BytesLine(
        title=u"Role",
        description=u"Specifies the Role to be mapped.",
        required=False)
