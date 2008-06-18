##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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
"""Infos about utilities.
"""
from zope.component import globalregistry

class UtilityInfo(object):

    def __init__(self, obj=None):
        self.context = obj

    def getAllUtilities(self):
        return [
            dict(name=x.name, provided=x.provided,
                 registry=x.registry, component=x.component)
            for x in list(globalregistry.base.registeredUtilities())]
