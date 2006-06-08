##############################################################################
#
# Copyright (c) 2005, 2006 Zope Corporation and Contributors.
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

"""
$Id$
"""

__docformat__ = 'restructuredtext'

from zope.component.interface import provideInterface
from zope.schema.interfaces import IDict
from zope.schema.interfaces import ISequence
from zope.schema.interfaces import IObject

from zope.generic.configuration import IConfigurationType
from zope.generic.configuration import INestedConfiguration
from zope.generic.configuration import INestedConfigurationType



def configurationDirective(_context, keyface, nested=None):
    """Type configuration key interface by IConfiugrationType."""

    # assume that the correct type was set
    if IConfigurationType.providedBy(keyface):
        return

    type = IConfigurationType
    if nested:
        type = INestedConfigurationType

    # evaluate if nested
    elif nested is None:
        for name in keyface:
            field = keyface[name]
            if INestedConfiguration.providedBy(field):
                type = INestedConfigurationType
                break

    provideInterface(None, keyface, type)
