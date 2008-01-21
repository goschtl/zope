##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
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
__docformat__ = 'restructuredtext'

import unittest
import zope.interface
from zope.interface.verify import verifyClass
from zope.app.testing import placelesssetup

from z3c.language.switch import IReadI18n
from z3c.language.switch import IWriteI18n
from z3c.language.switch import II18n
from z3c.language.switch import II18nLanguageSwitch
from z3c.testing import InterfaceBaseTest
from z3c.testing import marker_pos
from z3c.testing import marker_kws

def sorted(list):
    list.sort()
    return list


################################################################################
#
# Public Test implementations
#
################################################################################

class IContentObject(zope.interface.Interface):
    """IContentObject interface."""


class II18nContentObject(zope.interface.Interface):
    """II18nContentObject interface."""


class ContentObject(object):
    """Content type."""

    zope.interface.implements(IContentObject)

    __parent__ = __name__ = None
    
    _title = u''

    def __init__(self, title=''):
        self._title = title

    def getTitle(self):
        """Get the title of the object."""
        return self._title

    def setTitle(self, title):
        """Set the title of the object."""
        self._title = title

    title = property(getTitle, setTitle)


class I18nContentObject(object):
    """i18n content type."""

    zope.interface.implements(II18nContentObject, IReadI18n, IWriteI18n)

    def __init__(self, title='', defaultLanguage=None):
        self._data = {}
        if defaultLanguage == None:
            self._defaultLanguage = 'en'
        else:
            self._defaultLanguage = defaultLanguage
        document = self._create(title)
        self._data[self._defaultLanguage] = document

    def getTitle(self, language=None):
        """Get the title of the object."""
        document = self._get_or_add(language)
        return document.title

    def setTitle(self, title, language=None):
        """Set the title of the object."""
        document = self._get_or_add(language)
        document.title = title

    title = property(getTitle, setTitle)

    # IReadI18n interface
    def getAvailableLanguages(self):
        """See `z3c.langauge.switch.interfaces.IReadI18n`"""
        keys = self._data.keys()
        keys.sort()
        return keys

    def getDefaultLanguage(self):
        """See `z3c.langauge.switch.interfaces.IReadI18n`"""
        return self._defaultLanguage

    # IWriteI18n interface
    def setDefaultLanguage(self, language):
        """See `z3c.langauge.switch.interfaces.IWriteI18n`"""
        if language not in self._data:
            raise ValueError(
                  'cannot set nonexistent language (%s) as default' % language)
        self._defaultLanguage = language

    def addLanguage(self, language, title=''):
        """See `z3c.langauge.switch.interfaces.IWriteI18n`"""
        return self._get_or_add(language, title)

    def removeLanguage(self, language):
        """See `z3c.langauge.switch.interfaces.IWriteI18n`"""
        if language == self.getDefaultLanguage():
            raise ValueError('cannot remove default language (%s)' % language)
        elif language not in self._data:
            raise ValueError('cannot remove nonexistent language (%s)' 
                % language)
        else:
            del self._data[language]
            self._p_changed = True

    # helper methods
    def _create(self, title=''):
        """Create a new subobject of the type document."""
        return ContentObject(title)

    def _get(self, language):
        """Helper function -- return a subobject for a given language,
        and if it does not exist, return a subobject for the default
        language.
        """
        document = self._data.get(language)
        if not document:
            document = self._data[self.getDefaultLanguage()]
        return document

    def _get_or_add(self, language, title=''):
        """Helper function -- return a subobject for a given language,
        and if it does not exist, create and return a new subobject.
        """
        language = self._getLang(language)
        document = self._data.get(language)
        if not document:
            document = self._create(title)
            self._data[language] = document
            self._p_changed = 1
        return document

    def _getLang(self, language):
        """Returns the given language or the default language."""
        if language == None:
            language = self.getDefaultLanguage()

        return language


class I18nContentObjectLanguageSwitch(object):
    """Language switch for I18nContentObject."""
    
    zope.interface.implements(II18nLanguageSwitch, II18nContentObject)

    _language = 'en'

    def __init__(self, context):
        self.context = context
        self._language = context.getDefaultLanguage()

    # II18nLanguageSwitch interface
    def getLanguage(self):
        """See `z3c.langauge.switch.interfaces.II18nLanguageSwitch`"""
        return self._language

    def setLanguage(self, language):
        """See `z3c.langauge.switch.interfaces.II18nLanguageSwitch`"""
        self._language = language

    # II18nContentObject interface
    def getTitle(self):
        """Get the title of the object."""
        return self.context.getTitle(self.getLanguage())

    def setTitle(self, title):
        """Set the title of the object."""
        self.context.setTitle(title, self.getLanguage())

    title = property(getTitle, setTitle)


################################################################################
#
# Public Base Tests
#
################################################################################

class BaseTestII18n(InterfaceBaseTest):

    def getTestInterface(self):
        raise NotImplementedError, \
            'Subclasses has to implement getTestInterface()'

    def makeI18nTestObject(self, **kws):
        kws['defaultLanguage'] = kws.get('defaultLanguage', 'de')
        return self.makeTestObject(**kws)

    # IReadI18n tests
    def test_getAvailableLanguages(self):
        i18n = self.makeI18nTestObject()
        res = ['de']
        self.assertEqual(sorted(i18n.getAvailableLanguages()), res)

    def test_getDefaultLanguage(self):
        i18n = self.makeI18nTestObject()
        self.assertEqual(i18n.getDefaultLanguage(), 'de')

    # IWriteI18n tests
    def test_setDefaultLanguage(self):
        i18n = self.makeI18nTestObject()
        self.assertEqual(i18n.getDefaultLanguage(), 'de')
        i18n.addLanguage('en')
        i18n.setDefaultLanguage('en')
        self.assertEqual(i18n.getDefaultLanguage(), 'en')

    def test_addLanguage(self):
        i18n = self.makeI18nTestObject()
        i18n.addLanguage('at')
        res = ['at', 'de']
        self.assertEqual(sorted(i18n.getAvailableLanguages()), res)

    def test_removeLanguage(self):
        i18n = self.makeI18nTestObject()
        i18n.addLanguage('fr')
        res = ['de', 'fr']
        self.assertEqual(sorted(i18n.getAvailableLanguages()), res)
        i18n.removeLanguage('fr')
        res = ['de']
        self.assertEqual(sorted(i18n.getAvailableLanguages()), res)
        self.assertRaises(ValueError, i18n.removeLanguage, 'de')
        self.assertRaises(ValueError, i18n.removeLanguage, 'undefined')

    def test_II18n_Interface(self):
        i18n = self.makeI18nTestObject()
        class_ = self.getTestClass()
        self.failUnless(IReadI18n.implementedBy(class_))
        self.failUnless(IWriteI18n.implementedBy(class_))
        self.failUnless(II18n.implementedBy(class_))
        self.failUnless(verifyClass(IReadI18n, class_))
        self.failUnless(verifyClass(IWriteI18n, class_))
        self.failUnless(verifyClass(II18n, class_))


class BaseTestI18nLanguageSwitch(InterfaceBaseTest):

    def getTestClass(self):
        raise NotImplementedError, \
            'Subclasses has to implement getTestClass()'

    def getTestInterface(self):
        raise NotImplementedError, \
            'Subclasses has to implement getTestInterface()'

    def getAdaptedClass(self):
        raise NotImplementedError, \
            'Subclasses has to implement getAdaptedClass()'
    
    def makeTestObject(self, object=None, *pos, **kws):
        # provide default positional or keyword arguments
        if self.getTestPos() is not marker_pos and not pos:
            pos = self.getTestPos()

        if self.getTestKws() is not marker_kws and not kws:
            kws = self.getTestKws()
       
        testclass = self.getAdaptedClass()
        iface = self.getTestInterface()
        
        if object is None:
            # a class instance itself is the object to be tested.         
            obj = testclass(*pos, **kws)
            return iface(obj)

        else:
            # an adapted instance is the object to be tested. 
            obj = testclass(object, *pos, **kws)
            return iface(obj)

    def setUp(self):
        placelesssetup.setUp()
        factory = self.getTestClass()
        iface = self.getTestInterface()
        required = self.getAdaptedClass()
        # register language switch for test interface adapter
        zope.component.provideAdapter(factory, (required,), iface)

    def tearDown(self):
        placelesssetup.tearDown()

    def test_getLanguage(self):
        obj = self.makeTestObject()
        self.assertEqual(obj.getLanguage(), 'de')

    def test_setLanguage(self):
        obj = self.makeTestObject()
        obj.setLanguage('fr')
        self.assertEqual(obj.getLanguage(), 'fr')

    def test_i18n_II18nLanguageSwitch_Interface(self):
        class_ = self.getTestClass()
        obj = self.makeTestObject()
        iface = self.getTestInterface()
        adapter = iface(obj)
        self.failUnless(II18nLanguageSwitch.implementedBy(class_))
        self.failUnless(verifyClass(II18nLanguageSwitch, class_))
        self.failUnless(iface.providedBy(adapter))
