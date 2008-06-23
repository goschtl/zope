##############################################################################
#
# Copyright (c) 2007-2008 Zope Foundation and contributors.
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
"""Unit test support."""

import ZODB.DemoStorage
import ZODB.config


class Opener(ZODB.config.BaseConfig):

    def open(self):
        name = self.config.name
        return DumbStorage(name)


class DumbStorage(ZODB.DemoStorage.DemoStorage):

    def __init__(self, name=''):
        ZODB.DemoStorage.DemoStorage.__init__(self)
        self._name = name
        self._log = []

    def getSize(self):
        self._log.append("Storage '%s' called." % self._name)
        ZODB.DemoStorage.DemoStorage.getSize(self)

    def supportsUndo(self):
        return True