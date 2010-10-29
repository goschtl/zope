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
"""TAN Generator Implementation

$Id$
"""
__docformat__ = "reStructuredText"
import random
import zope.component
import zope.interface
from zope.schema.fieldproperty import FieldProperty

from z3c.tan import interfaces, tan

class CommonTANGenerator(object):
    zope.interface.implements(interfaces.ICommonTANGenerator)

    length = FieldProperty(interfaces.ICommonTANGenerator['length'])
    characters = FieldProperty(interfaces.ICommonTANGenerator['characters'])

    def __init__(self, seed=0):
        self._random = random.Random(seed)

    def generate(self, manager, amount=1, title=None, description=None,
                 allowedPrincipals=None):
        all = []
        for i in xrange(amount):
            added = False
            # Loop to catch duplicates
            while not added:
                tanStr = u''.join(
                    self._random.sample(self.characters, self.length))
                tanObj = tan.TANInformation(tanStr, title, description)
                tanObj.allowedPrincipals = allowedPrincipals
                try:
                    manager.add(tanObj)
                except interfaces.TANAlreadyUsed:
                    continue
                else:
                    all.append(tanStr)
                    added = True
        return all

