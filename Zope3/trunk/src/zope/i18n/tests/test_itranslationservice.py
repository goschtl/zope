##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""This is an 'abstract' test for the ITranslationService interface.

$Id: test_itranslationservice.py,v 1.1 2003/03/25 23:25:15 bwarsaw Exp $
"""

import unittest
from zope.interface.verify import verifyObject
from zope.component.tests.placelesssetup import PlacelessSetup

# XXX Bad, can't depend on app!
from zope.app.component.metaconfigure import provideService, managerHandler
from zope.i18n.negotiator import negotiator
from zope.i18n.interfaces import INegotiator
from zope.i18n.interfaces import IUserPreferredLanguages
from zope.i18n.interfaces import ITranslationService


class Environment:

    __implements__ = IUserPreferredLanguages

    def __init__(self, langs=()):
        self.langs = langs

    def getPreferredLanguages(self):
        return self.langs



class TestITranslationService(PlacelessSetup, unittest.TestCase):

    # This should be overwritten by every clas that inherits this test
    def _getTranslationService(self):
        pass

    def setUp(self):
        PlacelessSetup.setUp(self)
        self._service = self._getTranslationService()
        assert verifyObject(ITranslationService, self._service)
        # Setup the negotiator service registry entry
        managerHandler('defineService', 'LanguageNegotiation', INegotiator)
        provideService('LanguageNegotiation', negotiator, 'zope.Public')

    # I know, I know. This is not part of the interface, but it is implemented
    # in every Translation Service, so it fits well here.
    def testInterpolation(self):
        service = self._service
        interp = service.interpolate
        eq = self.assertEqual
        mapping = {'name': 'Zope', 'version': '3x'}
        # Test simple interpolations
        eq(interp('This is $name.', mapping), 'This is Zope.')
        eq(interp('This is ${name}.', mapping), 'This is Zope.')
        # Test more than one interpolation variable
        eq(interp('This is $name version $version.', mapping),
           'This is Zope version 3x.')
        eq(interp('This is ${name} version $version.', mapping),
           'This is Zope version 3x.')
        eq(interp('This is $name version ${version}.', mapping),
           'This is Zope version 3x.')
        eq(interp('This is ${name} version ${version}.', mapping),
           'This is Zope version 3x.')
        # Test escaping the $
        eq(interp('This is $$name.', mapping), 'This is $$name.')
        eq(interp('This is $${name}.', mapping), 'This is $${name}.')

    def testSimpleTranslate(self):
        translate = self._service.translate
        eq = self.assertEqual
        # Test that a given message id is properly translated in a supported
        # language
        eq(translate('default', 'short_greeting', target_language='de'),
           'Hallo!')
        # Same test, but use the context argument
        context = Environment(('de', 'en'))
        eq(translate('default', 'short_greeting', context=context),
           'Hallo!')

    def testDynamicTranslate(self):
        translate = self._service.translate
        eq = self.assertEqual
        # Testing both translation and interpolation
        eq(translate('default', 'greeting', mapping={'name': 'Stephan'},
                     target_language='de'),
           'Hallo Stephan, wie geht es Dir?')

    def testNoTranslation(self):
        translate = self._service.translate
        eq = self.assertEqual
        # Test that an unknown message id returns None as a translation
        eq(translate('default', 'glorp_smurf_hmpf', target_language='en'),
           None)

def test_suite():
    return unittest.TestSuite() # Deliberatly empty
