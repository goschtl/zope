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
"""Local Object Hub"""

from Zope.ComponentArchitecture import getService
from Zope.Proxy.ContextWrapper import isWrapper
from Zope.App.Traversing import getPhysicalPathString
from Zope.App.Traversing import locationAsUnicode

def normalizeToHubIds(context, *args):
    """given a context and any number of hub ids, physical paths,
    or wrapped objects, returns a normalized list of each item as hubid
    using the ObjectHub closest to the context.
    """
    obHub = getService(context, "ObjectHub")
    args = list(args)
    for ix in len(args):
        arg = args[ix]
        if isinstance(arg, int):
            pass
        elif isinstance(arg, str):
            args[ix] = obHub.lookupHubId(locationAsUnicode(arg))
        elif isWrapper(arg):
            args[ix] = getPhysicalPathString(arg)
    return args