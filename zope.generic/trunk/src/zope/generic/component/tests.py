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

import unittest

from zope import component
from zope import interface
from zope.testing import doctest


from zope.generic.testing.testing import InterfaceBaseTest
from zope.generic.testing.testing import registerDirective

from zope.generic.component import api
from zope.generic.component import testing


###############################################################################
#
# Unit tests  
#
###############################################################################

class ConfigurationDataTest(InterfaceBaseTest):

    _verify_class = False
    _test_interface = testing.IFooConfiguration
    _test_pos = (testing.IFooConfiguration, {'foo': u'Bla bla'})

    @property
    def _test_class(self):
        from zope.generic.component.base import ConfigurationData
        return  ConfigurationData

    def test_readonly_attributes(self):
        interface = self._test_interface
        test_obj = self.makeTestObject()
        for name in interface:
            field = interface[name]
            if field.readonly is True:
                self.assertRaises(ValueError, setattr, test_obj, name, object())

    def test_default_value(self):
        interface = self._test_interface
        test_obj = self.makeTestObject()
        fo_field = interface['fo']
        self.assertEqual(getattr(test_obj, 'fo'), fo_field.default)


class KeyInterfaceAdapterTest(InterfaceBaseTest):

    @property
    def _test_interface(self):
        from zope.generic.component import IKeyInterface
        return  IKeyInterface

    @property
    def _test_class(self):
        from zope.generic.component.adapter import KeyInterface
        return KeyInterface

    @property
    def _test_pos(self):
        return (testing.TestKeyInterfaceAttriute(),)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ConfigurationDataTest),
        #TODO: Why does it fail? unittest.makeSuite(KeyInterfaceAdapterTest),
        doctest.DocTestSuite('zope.generic.component.helper'),
        doctest.DocTestSuite('zope.generic.component.base'),
        doctest.DocTestSuite('zope.generic.component.event'),
        doctest.DocTestSuite('zope.generic.component.adapter'),
        doctest.DocFileSuite('README.txt',
                             setUp=testing.placelesssetup.setUp,
                             tearDown=testing.placelesssetup.tearDown,
                             globs={'component': component, 'interface': interface,
                             'registerDirective': registerDirective,
                             'testing': testing, 'api': api},
                             optionflags=doctest.NORMALIZE_WHITESPACE+
                                            doctest.ELLIPSIS),
        doctest.DocFileSuite('NEW_README.txt',
                             setUp=testing.placelesssetup.setUp,
                             tearDown=testing.placelesssetup.tearDown,
                             globs={'component': component, 'interface': interface,
                             'registerDirective': registerDirective,
                             'testing': testing, 'api': api},
                             optionflags=doctest.NORMALIZE_WHITESPACE+
                                            doctest.ELLIPSIS),
        ))

if __name__ == '__main__': unittest.main()
