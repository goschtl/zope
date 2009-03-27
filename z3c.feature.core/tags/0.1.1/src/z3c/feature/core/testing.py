##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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
"""Testing Support

$Id$
"""


class EntryPoint(object):

    def __init__(self, group, name, klass, dist):
        self.group = group
        self.name = name
        self.klass = klass
        self.dist = dist

    def load(self):
        return self.klass

class FeatureDistribution(object):

    project_name = 'z3c.feature.testing'
    key = 'z3c.feature.testing'
    location = 'z3c.feature.testing'

    def __init__(self):
        self.entryPoints = {}

    def addEntryPoint(self, group, name, klass):
        eps = self.entryPoints.setdefault(group, {})
        eps[name] = EntryPoint(group, name, klass, self)

    def get_entry_map(self, group):
        return self.entryPoints[group]

    def insert_on(self, entries, entry):
        entries.append(self.location)

    def activate(self):
        pass
