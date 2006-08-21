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

from persistent import Persistent
from zope.interface import implements

from zope.component import ComponentLookupError

from zope.i18n.interfaces import IUserPreferredLanguages
from zope.i18n.negotiator import negotiator

from zope.app.zapi import getUtility
from zope.app.container.contained import Contained

from zope.app.session.session import Session
from zope.app.session.interfaces import ISession
from zope.app.session.interfaces import IClientId
from zope.app.session.interfaces import ISessionDataContainer
from zope.app.session.session import SessionData
from zope.app.session.session import SessionPkgData

from z3c.language.session import ILanguageSession
from z3c.language.session import IGetLanguage
from z3c.language.session import ISetLanguage
from z3c.language.session import sessionPkgDataId



class LanguageSession(Session):
    """Handles i18n language via server session.

    >>> from zope.app.session.interfaces import ISession
    >>> from zope.app.session.session import PersistentSessionDataContainer
    >>> from zope.app.session import tests
    >>> request = tests.setUp(PersistentSessionDataContainer)
    >>> request2 = tests.HTTPRequest(None, {}, None)

    >>> ILanguageSession.providedBy(LanguageSession(request))
    True

    >>> ISession.providedBy(LanguageSession(request))
    True

    Setup a language sessions:

    >>> sessionLanguage = LanguageSession(request)

    Test getLanguage, if no language is set, it should be None:

    >>> sessionLanguage.getLanguage()

    Test setLanguage:

    >>> sessionLanguage.setLanguage('de')
    >>> sessionLanguage.getLanguage()
    'de'

    >>> tests.tearDown()

    """

    implements(ILanguageSession, IGetLanguage, ISetLanguage)

    def __init__(self, request):
        super(LanguageSession, self).__init__(request)

    def getLanguage(self):
        """Returns the language form the session."""
        spd = self.__getitem__(sessionPkgDataId)
        lang = spd.get('language', None)
        if lang:
            return lang
        else:
            return None

    def setLanguage(self, language):
        """Set the language to the session."""
        spd = self.__getitem__(sessionPkgDataId)
        spd['language'] = language
