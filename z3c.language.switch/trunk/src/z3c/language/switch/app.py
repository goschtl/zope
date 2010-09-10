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

import persistent
import zope.interface
import zope.component
import zope.event
import zope.lifecycleevent
from zope.i18n.interfaces import INegotiator
from zope.security.interfaces import NoInteraction
from zope.security.management import getInteraction

from z3c.language.switch import II18n


def getRequest():
    try:
        interaction = getInteraction()
        request = interaction.participations[0]
    except NoInteraction:
        request = None
    except IndexError:
        request = None
    return request


class I18n(persistent.Persistent, object):
    """Mixin implementation of II18n.

    Set a factory class in our implementation. The _create method will initalize
    this class and use it as a child object providing the attributes without
    languages.

    You can use this class as mixin for i18n implementations:

    >>> from z3c.language.switch.app import I18n
    >>> class Person(object):
    ...     def __init__(self, firstname, lastname):
    ...         self.firstname = firstname
    ...         self.lastname = lastname

    >>> class I18nPerson(I18n):
    ...     _defaultLanguage = 'en'
    ...     _factory = Person

    Now you can initialize the default translation:

    >>> i18n = I18nPerson(firstname='Bob', lastname='Miller')
    >>> i18n.getDefaultLanguage()
    'en'
    >>> i18n.getPreferedLanguage()
    'en'

    You can access the attributes of the default translation:

    >>> i18n.getAttribute('firstname')
    'Bob'
    >>> i18n.getAttribute('lastname')
    'Miller'

    That is the same as accessing the attribute using a language parameter:

    >>> i18n.getAttribute('firstname', 'en')
    'Bob'

    If an attribute is not available a AttributeError is raised. The
    queryAttribute method offers a save way for unsecure access:

    >>> i18n.getAttribute('name')
    Traceback (most recent call last):
    ...
    AttributeError: 'Person' object has no attribute 'name'

    >>> i18n.queryAttribute('name') is None
    True

    If the given language is not available a KeyError is raised. The
    queryAttribute method offers a save way for unsecure access:

    >>> i18n.getAttribute('firstname', 'zh') is None
    Traceback (most recent call last):
    ...
    KeyError: 'zh'

    >>> i18n.queryAttribute('firstname', 'zh') is None
    True

    You can set the attributes an other time:

    >>> i18n.setAttributes('en', firstname='Foo', lastname='Bar')
    >>> i18n.getAttribute('firstname')
    'Foo'
    >>> i18n.getAttribute('lastname')
    'Bar'

    You can initialize the default translation using a specific language:

    >>> i18n = I18nPerson(defaultLanguage='fr', firstname='Robert',
    ...                   lastname='Moulin')
    >>> i18n.getDefaultLanguage()
    'fr'
    >>> i18n.getPreferedLanguage()
    'fr'

    """

    _data = None
    # sublclasses should overwrite this attributes.
    _defaultLanguage = None
    _factory = None

    # private method (subclasses might overwrite this method)
    def _defaultArgs(self):
        return None

    zope.interface.implements(II18n)


    def __init__(self, defaultLanguage=None, *args, **kws):
        # preconditions
        if self._defaultLanguage is None:
            raise NotImplementedError('_defaultLanguage')

        if self._factory is None:
            raise NotImplementedError('_factory')

        # essentials
        if defaultLanguage is None:
            defaultLanguage = self._defaultLanguage

        # initialize data store for translations
        self._setDataOnce()

        # initialize default translation
        self._get_or_add(defaultLanguage, *args, **kws)

        # set default language
        self.setDefaultLanguage(defaultLanguage)

    # private method
    def _setDataOnce(self):
        if self._data is None:
            self._data = {}

    # private method: access self._data only using this method
    def _getData(self):
        return self._data

    # z3c.langauge.switch.IReadI18n
    def getAvailableLanguages(self):
        """See `z3c.langauge.switch.interfaces.IReadI18n`"""
        keys = self._getData().keys()
        keys.sort()
        return keys

    def getDefaultLanguage(self):
        """See `z3c.langauge.switch.interfaces.IReadI18n`"""
        return self._defaultLanguage

    def getPreferedLanguage(self):
        # evaluate the negotiator
        language = None
        request = getRequest()
        negotiator = None
        try:
            negotiator = zope.component.queryUtility(INegotiator,
                name='', context=self)
        except zope.component.ComponentLookupError:
            # can happens during tests without a site and sitemanager
            pass
        if request and negotiator:
            language = negotiator.getLanguage(self.getAvailableLanguages(), request)
        if language is None:
            language = self.getDefaultLanguage()
        if language is None:
            # fallback language for functional tests, there we have a cookie request
            language = 'en'
        return language

    def getAttribute(self, name, language=None):
        # preconditions
        if language is None:
            language = self.getDefaultLanguage()

        if not language in self.getAvailableLanguages():
            raise KeyError(language)

        # essentials
        data = self._getData()[language]
        return getattr(data, name)

    def queryAttribute(self, name, language=None, default=None):
        try:
            return self.getAttribute(name, language)
        except (KeyError, AttributeError):
            return default

    # z3c.langauge.switch.IReadI18n
    def setDefaultLanguage(self, language):
        """See `z3c.langauge.switch.interfaces.IWriteI18n`"""
        data = self._getData()
        if language not in data:
            raise ValueError(
                'cannot set nonexistent language (%s) as default' % language)
        self._defaultLanguage = language

    def addLanguage(self, language, *args, **kw):
        """See `z3c.langauge.switch.interfaces.IWriteI18n`"""
        if not args and not kw:
            if self._defaultArgs() is not None:
                args = self._defaultArgs()

        self._get_or_add(language, *args, **kw)
        zope.event.notify(zope.lifecycleevent.ObjectModifiedEvent(self))

    def removeLanguage(self, language):
        """See `z3c.langauge.switch.interfaces.IWriteI18n`"""
        data = self._getData()
        if language == self.getDefaultLanguage():
            raise ValueError('cannot remove default language (%s)' % language)
        elif language not in data:
            raise ValueError('cannot remove nonexistent language (%s)'
                % language)
        else:
            del data[language]
            self._p_changed = True
        zope.event.notify(zope.lifecycleevent.ObjectModifiedEvent(self))

    def setAttributes(self, language, **kws):
        # preconditions
        if not language in self.getAvailableLanguages():
            raise KeyError(language)

        data = self._getData()
        obj = data[language]

        for key in kws:
            if not hasattr(obj, key):
                raise KeyError(key)

        # essentials
        for key in kws:
            setattr(obj, key, kws[key])
        else:
            self._p_changed = True
        zope.event.notify(zope.lifecycleevent.ObjectModifiedEvent(self))

    # private helper methods
    def _create(self, *args, **kw):
        """Create a new subobject of the type document."""
        factory = self._factory
        obj = factory(*args, **kw)
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(obj))
        return obj

    def _get(self, language):
        """Helper function -- return a subobject for a given language,
        and if it does not exist, return a subobject for the default
        language.
        """
        data = self._getData()
        obj = data.get(language, None)
        if obj is None:
            obj = data[self.getDefaultLanguage()]
        return obj

    def _get_or_add(self, language, *args, **kw):
        """Helper function -- return a subobject for a given language,
        and if it does not exist, create and return a new subobject.
        """
        data = self._getData()
        language = self._getLang(language)
        obj = data.get(language, None)
        if obj is None:
            obj = self._create(*args, **kw)
            data[language] = obj
            # this (ILocation info) is needed for the pickler used by the
            # locationCopy method in the ObjectCopier class
            obj.__parent__ = self
            obj.__name__ = language
            self._p_changed = 1
        return obj

    def _getLang(self, language):
        """Returns the given language or the default language."""
        if language == None:
            language = self.getDefaultLanguage()

        return language
