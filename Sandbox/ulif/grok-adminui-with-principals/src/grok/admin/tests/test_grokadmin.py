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
"""Setup for tests."""

import unittest
from pkg_resources import resource_listdir
from zope.testing import doctest, cleanup
import zope.component.eventtesting
from zope.annotation.attribute import AttributeAnnotations
from zope.app.authentication.interfaces import IPasswordManager
from zope.app.authentication.password import PlainTextPasswordManager
from zope.app.authentication.password import MD5PasswordManager
from zope.app.authentication.password import SHA1PasswordManager
from zope.app.testing import ztapi

def setUpZope(test):
    zope.component.eventtesting.setUp(test)
    zope.component.provideAdapter(AttributeAnnotations)
    # The auth tests require available password managers:
    ztapi.provideUtility(IPasswordManager, PlainTextPasswordManager(),
                                  "Plain Text")
    ztapi.provideUtility(IPasswordManager, MD5PasswordManager(),
                                  "MD5")
    ztapi.provideUtility(IPasswordManager, SHA1PasswordManager(),
                                  "SHA1")

def cleanUpZope(test):
    cleanup.cleanUp()

def suiteFromPackage(name):
    files = resource_listdir(__name__, name)
    suite = unittest.TestSuite()
    for filename in files:
        if not filename.endswith('.py'):
            continue
        if filename.endswith('_fixture.py'):
            continue
        if filename == '__init__.py':
            continue

        dottedname = 'grok.admin.tests.%s.%s' % (name, filename[:-3])
        test = doctest.DocTestSuite(dottedname,
                                    setUp=setUpZope,
                                    tearDown=cleanUpZope,
                                    optionflags=doctest.ELLIPSIS+
                                    doctest.NORMALIZE_WHITESPACE)

        suite.addTest(test)
    return suite

def test_suite():
    suite = unittest.TestSuite()
    for name in []:
        suite.addTest(suiteFromPackage(name))
    for name in ['docgrok.txt', 'objectinfo.txt', 'utilities.py', 'auth.txt']:
        suite.addTest(doctest.DocFileSuite(name,
                                           package='grok.admin',
                                           setUp=setUpZope,
                                           tearDown=cleanUpZope,
                                           optionflags=doctest.ELLIPSIS+
                                           doctest.NORMALIZE_WHITESPACE)
                      )
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
