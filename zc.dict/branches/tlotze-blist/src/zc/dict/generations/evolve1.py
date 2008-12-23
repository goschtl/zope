##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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

import zope.app.generations.utility

import zc.blist
import zc.dict


generation = 1


def evolve(context):
    root = context.connection.root()
    for obj in zope.app.generations.utility.findObjectsMatching(
        root, lambda obj: isinstance(obj, zc.dict.OrderedDict)):
        if type(obj._order) is not zc.blist.BList:
            obj._order = zc.blist.BList(obj._order)
