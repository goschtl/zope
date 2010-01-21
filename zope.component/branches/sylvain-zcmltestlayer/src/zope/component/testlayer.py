##############################################################################
#
# Copyright (c) 2010 Zope Corporation and Contributors.
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

import os

from zope.configuration import xmlconfig, config
from zope.testing.cleanup import cleanUp

class ZCMLLayer(object):
    """Base layer in order to load a ZCML configuration.
    """

    __bases__ = ()

    def __init__(self, package, name=None, zcml_file='ftesting.zcml'):
        if name is None:
            name = self.__class__.__name__
        self.__name__ = name
        self.__module__ = package.__name__
        self.zcml_file = os.path.join(
            os.path.dirname(package.__file__), zcml_file)
        self.features = ()

    def setUp(self):
        zope.component.hooks.setHooks()
        context = config.ConfigurationMachine()
        xmlconfig.registerCommonDirectives(context)
        for feature in self.features:
            context.provideFeature(feature)
        context = xmlconfig.file(self.zcml_file, context=context, execute=True)

    def tearDown(self):
        cleanUp()
