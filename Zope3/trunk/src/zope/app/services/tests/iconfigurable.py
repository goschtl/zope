##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""XXX short summary goes here.

XXX longer description goes here.

$Id: iconfigurable.py,v 1.2 2002/12/25 14:13:20 jim Exp $
"""
from zope.app.interfaces.services.configuration import IConfigurable
from zope.interface.verify import verifyObject
from zope.proxy.context import getWrapperContainer

class TestingIConfigurable:
    """Base class for testing implementors of IConfigurable

    Subclasses must implement:

      - createTestingConfigurable()
        that returns a new configurable object with no configurations.

        This configuration object must be in the context of something
        that is not None.

      - createTestingConfiguration()
        that returns a configuration object.

    """

    def _assertInContext(self, ob, parent):
        """Assert that we have the proper context

        The container of ob must be the parent, and the parent must
        have some context.

        """
        self.assertEqual(getWrapperContainer(ob), parent)
        self.failIf(getWrapperContainer(getWrapperContainer(ob)) is None)

    def test_implements_IConfigurable(self):
        verifyObject(IConfigurable, self.createTestingConfigurable())

    def test_queryConfigurationsFor_no_config(self):
        configurable = self.createTestingConfigurable()
        configuration = self.createTestingConfiguration()
        self.failIf(configurable.queryConfigurationsFor(configuration))

        self.assertEqual(
            configurable.queryConfigurationsFor(configuration, 42),
            42)

    def test_createConfigurationsFor(self):
        configurable = self.createTestingConfigurable()
        configuration = self.createTestingConfiguration()
        registry = configurable.createConfigurationsFor(configuration)

        self.assertEqual(getWrapperContainer(registry), configurable)

        # If we call it again, we should get the same object
        self.assertEqual(configurable.createConfigurationsFor(configuration),
                         registry)

        self._assertInContext(registry, configurable)

        return registry

    def test_queryConfigurationsFor(self):
        configurable = self.createTestingConfigurable()
        configuration = self.createTestingConfiguration()

        cregistry = configurable.createConfigurationsFor(configuration)


        registry = configurable.queryConfigurationsFor(configuration)
        self.assertEqual(registry, cregistry)
        self._assertInContext(registry, configurable)

        registry = configurable.queryConfigurationsFor(configuration, 42)
        self.assertEqual(registry, cregistry)
        self._assertInContext(registry, configurable)
