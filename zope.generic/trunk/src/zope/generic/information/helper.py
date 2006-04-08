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

from zope.component import getUtility
from zope.component import getUtilitiesFor

from zope.generic.configuration.api import resolveClass



def dottedName(klass):
    if klass is None:
        return 'None'
    return klass.__module__ + '.' + klass.__name__



def getInformation(interface, registry):
    return getUtility(registry, dottedName(interface))



def queryInformation(interface, registry, default=None):
    try:
        return getInformation(interface, registry)

    except:
        return default


def registeredInformations(registry, default=None):
    for name, information in getUtilitiesFor(registry):
        yield (resolveClass(name), information)
