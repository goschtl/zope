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
"""Fssync Directive Schemas

$Id$
"""
from zope.configuration.fields import GlobalObject
from zope.interface import Interface

class IAdapterDirective(Interface):

    class_ = GlobalObject(
        title=u"Class",
        description=u"Specifies the class for which this adapter is " \
                    u"registered.",
        required=False)

    factory = GlobalObject(
        title=u"Factory",
        description=u"Specifies the factory that will create the adapter.",
        required=True)

