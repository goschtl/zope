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
"""
$Id: test_configurationmanager.py,v 1.4 2003/03/21 21:06:27 jim Exp $
"""

from zope.app.services.configuration import ConfigurationManager
from zope.app.interfaces.services.configuration import IConfigurationManager
from unittest import TestCase, TestSuite, main, makeSuite
from zope.interface.common.tests.basemapping import BaseTestIEnumerableMapping
from zope.interface.verify import verifyObject
from zope.app.interfaces.container import IDeleteNotifiable
from zope.app.interfaces.container import IContainer
from zope.app.interfaces.container import IZopeContainer
from zope.app.container.zopecontainer import ZopeContainerAdapter
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.component.adapter import provideAdapter


class Undeletable:

    __implements__ = IDeleteNotifiable

    def beforeDeleteHook(self, object, container):
        self.was_called = 1


class Test(BaseTestIEnumerableMapping, PlacelessSetup, TestCase):

    """Testing for Configuration Manager """

    def setUp(self):
        PlacelessSetup.setUp(self)
        self.__manager = manager = ConfigurationManager()
        for l in 'abcdefghijklmnop':
            manager.setObject('', l)
        del manager['8']
        del manager['10']

    def test_implements_IConfigurationManager(self):
        verifyObject(IConfigurationManager, self.__manager)

    def _IEnumerableMapping__stateDict(self):
        # Hook needed by BaseTestIEnumerableMapping
        # also, effectively test setObject and __delitem__.
        return {
            '1': 'a', '2': 'b', '3': 'c', '4': 'd', '5': 'e',
            '6': 'f', '7': 'g', '9': 'i', '11': 'k', '12': 'l',
            '13': 'm', '14': 'n', '15': 'o', '16': 'p',
            }

    def _IEnumerableMapping__sample(self):
        # Hook needed by BaseTestIEnumerableMapping
        # also, effectively test setObject and __delitem__.
        return self.__manager

    def _IEnumerableMapping__absentKeys(self):
        # Hook needed by BaseTestIEnumerableMapping
        # also, effectively test setObject and __delitem__.
        return ['-1', '8', '10', '17', '100', '10000']

    #########################################################
    # Move Top

    def test_moveTop_nothing(self):
        self.__manager.moveTop([])
        self.assertEqual(
            list(self.__manager.keys()),
            ['1', '2', '3', '4', '5', '6', '7', '9',
             '11', '12', '13', '14', '15', '16'],
            )

        # Make sure we still have thye right items
        self.test_items()

    def test_moveTop_1_no_effect(self):
        self.__manager.moveTop(['1'])
        self.assertEqual(
            list(self.__manager.keys()),
            ['1', '2', '3', '4', '5', '6', '7', '9',
             '11', '12', '13', '14', '15', '16'],
            )

        # Make sure we still have thye right items
        self.test_items()

    def test_moveTop_many_no_effect(self):
        self.__manager.moveTop(['1', '88', '3', '2', '99'])
        self.assertEqual(
            list(self.__manager.keys()),
            ['1', '2', '3', '4', '5', '6', '7', '9',
             '11', '12', '13', '14', '15', '16'],
            )

        # Make sure we still have thye right items
        self.test_items()

    def test_moveTop_1(self):
        self.__manager.moveTop(['3'])
        self.assertEqual(
            list(self.__manager.keys()),
            ['3', '1', '2', '4', '5', '6', '7', '9',
             '11', '12', '13', '14', '15', '16'],
            )

        # Make sure we still have thye right items
        self.test_items()

    def test_moveTop_many(self):
        self.__manager.moveTop(['1', '3', '88', '4', '11', '15', '16', '99'])
        self.assertEqual(
            list(self.__manager.keys()),
            ['1', '3', '4', '11', '15', '16', '2', '5', '6', '7', '9',
             '12', '13', '14'],
            )

        # Make sure we still have thye right items
        self.test_items()

    def test_moveTop_one_element_container(self):
        manager = ConfigurationManager()
        manager.setObject('', 'a')
        manager.moveTop(['1'])
        self.assertEqual(list(manager.items()), [('1', 'a')])

    #########################################################
    # Move Bottom

    def test_moveBottom_nothing(self):
        self.__manager.moveBottom([])
        self.assertEqual(
            list(self.__manager.keys()),
            ['1', '2', '3', '4', '5', '6', '7', '9',
             '11', '12', '13', '14', '15', '16'],
            )

        # Make sure we still have thye right items
        self.test_items()

    def test_moveBottom_1_no_effect(self):
        self.__manager.moveBottom(['16'])
        self.assertEqual(
            list(self.__manager.keys()),
            ['1', '2', '3', '4', '5', '6', '7', '9',
             '11', '12', '13', '14', '15', '16'],
            )

        # Make sure we still have thye right items
        self.test_items()

    def test_moveBottom_many_no_effect(self):
        self.__manager.moveBottom(['14', '88', '16', '15', '99'])
        self.assertEqual(
            list(self.__manager.keys()),
            ['1', '2', '3', '4', '5', '6', '7', '9',
             '11', '12', '13', '14', '15', '16'],
            )

        # Make sure we still have thye right items
        self.test_items()

    def test_moveBottom_1(self):
        self.__manager.moveBottom(['3'])
        self.assertEqual(
            list(self.__manager.keys()),
            ['1', '2', '4', '5', '6', '7', '9',
             '11', '12', '13', '14', '15', '16', '3'],
            )

        # Make sure we still have thye right items
        self.test_items()

    def test_moveBottom_many(self):
        self.__manager.moveBottom(
            ['1', '3', '88', '4', '11', '16', '15', '99'])
        self.assertEqual(
            list(self.__manager.keys()),
            ['2', '5', '6', '7', '9',
             '12', '13', '14', '1', '3', '4', '11', '15', '16'],
            )

        # Make sure we still have thye right items
        self.test_items()

    def test_moveBottom_one_element_container(self):
        manager = ConfigurationManager()
        manager.setObject('', 'a')
        manager.moveBottom(['1'])
        self.assertEqual(list(manager.items()), [('1', 'a')])

    #########################################################
    # Move Up

    def test_moveUp_nothing(self):
        self.__manager.moveUp([])
        self.assertEqual(
            list(self.__manager.keys()),
            ['1', '2', '3', '4', '5', '6', '7', '9',
             '11', '12', '13', '14', '15', '16'],
            )

        # Make sure we still have thye right items
        self.test_items()

    def test_moveUp_1_no_effect(self):
        self.__manager.moveUp(['1'])
        self.assertEqual(
            list(self.__manager.keys()),
            ['1', '2', '3', '4', '5', '6', '7', '9',
             '11', '12', '13', '14', '15', '16'],
            )

        # Make sure we still have thye right items
        self.test_items()

    def test_moveUp_many_no_effect(self):
        self.__manager.moveUp(['1', '88', '3', '2', '99'])
        self.assertEqual(
            list(self.__manager.keys()),
            ['1', '2', '3', '4', '5', '6', '7', '9',
             '11', '12', '13', '14', '15', '16'],
            )

        # Make sure we still have thye right items
        self.test_items()

    def test_moveUp_1(self):
        self.__manager.moveUp(['3'])
        self.assertEqual(
            list(self.__manager.keys()),
            ['1', '3', '2', '4', '5', '6', '7', '9',
             '11', '12', '13', '14', '15', '16'],
            )

        # Make sure we still have thye right items
        self.test_items()

    def test_moveUp_many(self):
        self.__manager.moveUp(
            ['1', '3', '88', '4', '11', '16', '15', '99'])
        self.assertEqual(
            list(self.__manager.keys()),
            ['1', '3', '4', '2', '5', '6', '7', '11', '9',
             '12', '13', '15', '16', '14'],
            )

        # Make sure we still have thye right items
        self.test_items()

    def test_moveUp_one_element_container(self):
        manager = ConfigurationManager()
        manager.setObject('', 'a')
        manager.moveUp(['1'])
        self.assertEqual(list(manager.items()), [('1', 'a')])

    #########################################################
    # Move Down

    def test_moveDown_nothing(self):
        self.__manager.moveDown([])
        self.assertEqual(
            list(self.__manager.keys()),
            ['1', '2', '3', '4', '5', '6', '7', '9',
             '11', '12', '13', '14', '15', '16'],
            )

        # Make sure we still have thye right items
        self.test_items()

    def test_moveDown_1_no_effect(self):
        self.__manager.moveDown(['16'])
        self.assertEqual(
            list(self.__manager.keys()),
            ['1', '2', '3', '4', '5', '6', '7', '9',
             '11', '12', '13', '14', '15', '16'],
            )

        # Make sure we still have thye right items
        self.test_items()

    def test_moveDown_many_no_effect(self):
        self.__manager.moveDown(['16', '88', '14', '15', '99'])
        self.assertEqual(
            list(self.__manager.keys()),
            ['1', '2', '3', '4', '5', '6', '7', '9',
             '11', '12', '13', '14', '15', '16'],
            )

        # Make sure we still have thye right items
        self.test_items()

    def test_moveDown_1(self):
        self.__manager.moveDown(['3'])
        self.assertEqual(
            list(self.__manager.keys()),
            ['1', '2', '4', '3', '5', '6', '7', '9',
             '11', '12', '13', '14', '15', '16'],
            )

        # Make sure we still have thye right items
        self.test_items()

    def test_moveDown_many(self):
        self.__manager.moveDown(
            ['1', '3', '88', '4', '11', '16', '15', '99'])
        self.assertEqual(
            list(self.__manager.keys()),
            ['2', '1', '5', '3', '4', '6', '7', '9',
             '12', '11', '13', '14', '15', '16'],
            )

        # Make sure we still have thye right items
        self.test_items()

    def test_moveDown_one_element_container(self):
        manager = ConfigurationManager()
        manager.setObject('', 'a')
        manager.moveDown(['1'])
        self.assertEqual(list(manager.items()), [('1', 'a')])

    #########################################################

    def test_manageBeforeDelete(self):
        provideAdapter(IContainer, IZopeContainer, ZopeContainerAdapter)
        container = []
        manager = ConfigurationManager()
        thingy = Undeletable()
        manager.setObject('xyzzy', thingy)
        manager.beforeDeleteHook(manager, container)
        self.failUnless(thingy.was_called)


def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
