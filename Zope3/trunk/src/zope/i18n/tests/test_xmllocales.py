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
# FOR A PARTLAR PURPOSE.
#
##############################################################################
"""Testing all XML Locale functionality.

$Id: test_xmllocales.py,v 1.6 2003/11/03 21:27:09 jeremy Exp $
"""
import os
from unittest import TestCase, TestSuite, makeSuite

from zope.i18n.locales import XMLLocaleFactory
from zope.i18n.format import parseDateTimePattern, parseNumberPattern

class LocaleXMLFileTestCase(TestCase):
    """This test verifies that every locale XML file can be loaded."""

    def __init__(self, path):
        self.__path = path
        TestCase.__init__(self)
        
    def runTest(self):
        # Loading Locale object 
        locale = XMLLocaleFactory(self.__path)()

        # Making sure all number format patterns parse
        for klass in locale.getNumberFormatClasses():
            format = locale.getNumberFormat(klass)
            for id in format.getAllPatternIds():
                self.assert_(
                    parseNumberPattern(format.getPattern(id)) is not None)

        # Making sure all datetime patterns parse
        for calendar in locale.calendars.values():
            for pattern in calendar.datePatterns.values():
                    self.assert_(parseDateTimePattern(pattern) is not None)
            for pattern in calendar.timePatterns.values():
                    self.assert_(parseDateTimePattern(pattern) is not None)
                    

##def test_suite():
##    suite = TestSuite()
##    locale_dir = os.path.join(os.path.dirname(zope.i18n.__file__), "locales")
##    for path in os.listdir(locale_dir):
##        if path.endswith(".xml"):
##            continue
##        path = os.path.join(locale_dir, path)
##        case = LocaleXMLFileTestCase(path)
##        suite.addTest(case)
##    return suite

# Note: These tests are disabled, just because they take a long time to run.
#       You should run these tests if you update the parsing code and/or
#       update the Locale XML Files.
def test_suite():
    return None
