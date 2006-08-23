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

from zope.i18n.interfaces import IUserPreferredLanguages
from zope.i18n.interfaces import INegotiator
from zope.i18n.negotiator import negotiator

from zope.app.container import contained

from z3c.language.session.interfaces import ILanguageSession

from z3c.language.negotiator.interfaces import INegotiatorManager
from z3c.language.negotiator.interfaces import language_policies



class Negotiator(persistent.Persistent, contained.Contained):
    """Loacal negotiator implementation.

    The negotiator let you change the policy, which is a alias
    for the lookup mechanism. 

    'server' -- The server defines the language

    'session' -- The session defines the language (usefull for testing)

    'browser' -- The browser defines the language (usefull for testing)

    'browser --> session --> server' -- Left criteria first

    'browser --> server' -- Left criteria first

    'session --> browser --> server' -- Left criteria first (default use case)

    'session --> server' -- Left criteria first

    The 'server' criteria is used as a fallback criteria in most use cases.

    """

    zope.interface.implements(INegotiator, INegotiatorManager)

    def __init__(self):
        self._policy = 'session --> browser --> server'
        self._serverLanguage = None
        self._sessionLanguages = []
        self._offeredLanguages = []

    def _getLanguagePolicy(self):
        """Returns the language policy."""
        return self._policy

    def _setLanguagePolicy(self, policy):
        """Set the language policy."""
        if policy not in language_policies:
            policies = str(language_policies)
            msg = "Only %s are valide policy names." % policies
            raise ValueError(msg, policy)
        self._policy = policy

    policy = property(_getLanguagePolicy, _setLanguagePolicy)

    def _getServerLanguage(self):
        """Returns the language for server policy."""
        return self._serverLanguage

    def _setServerLanguage(self, language):
        """Set the language for server policy."""
        self._serverLanguage = language

    serverLanguage = property(_getServerLanguage, _setServerLanguage)

    def _getSessionLanguages(self):
        """Returns the language for server policy."""
        return self._sessionLanguages

    def _setSessionLanguages(self, languages):
        """Set the language for server policy."""
        self._sessionLanguages = languages

    sessionLanguages = property(_getSessionLanguages, _setSessionLanguages)

    # TODO: 
    # perhaps we can make a relation to the translation domains
    # and dymanicly find out what language we support in the domains.
    def _getOfferedLanguages(self):
        """Returns the language for server policy."""
        return self._offeredLanguages

    def _setOfferedLanguages(self, languages):
        """Set the language for server policy."""
        self._offeredLanguages = languages

    offeredLanguages = property(_getOfferedLanguages, _setOfferedLanguages)

    def getLanguage(self, languages, request):
        """Returns the language dependent on the policy."""
        policyList = self._policy.split(' --> ')

        for policy in policyList:
            
            # the server is handling the language
            if policy == 'server':
                if self.serverLanguage:
                    return self.serverLanguage

            # the language is handled by a session 
            elif policy == 'session':
                session = ILanguageSession(request)
                lang = session.getLanguage()
                if lang != None:
                    return lang

            # the language is handled by the browsers language settings
            elif policy == 'browser':
                lang = negotiator.getLanguage(languages, request)
                if lang != None:
                    return lang

        return None
