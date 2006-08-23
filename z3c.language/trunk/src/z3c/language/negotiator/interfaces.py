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

import zope.interface
import zope.schema
from zope.schema.interfaces import IVocabularyTokenized

from zope.i18n.interfaces import INegotiator

from zope.app.session.interfaces import ISession

from z3c.i18n import MessageFactory as _

language_policies = ['server', 'session', 'browser', 
    'browser --> session --> server', 'browser --> server', 
    'session --> browser --> server', 'session --> server']


class INegotiatorManager(zope.interface.Interface):
    """Local negotiator utility manager interface."""

    policy = zope.schema.Choice(
        title=_("Language lookup policy"),
        description=_("Defines how the language lookup is working."),
        values=language_policies,
        default='session --> browser --> server',
        required=True)

    serverLanguage = zope.schema.TextLine(
        title=_(u"Server language"),
        description=_(u"The language used for server policy."),
        default=u"en",
        required=True,
        )

    sessionLanguages = zope.schema.List(
        title=_(u"Session languages"),
        description=_(u"A list of available languages in session policy."),
        value_type = zope.schema.TextLine(title=_(u"A i18n language."),
            description=_(u"""A i18n language definition string used in 
                sessions.""")),
        required=False,
        )

    offeredLanguages = zope.schema.List(
        title=_(u"Offered languages"),
        description=_(u"""A list of offered languages in the skin for the 
            user to select."""),
        value_type = zope.schema.TextLine(title=_(u"A i18n language."),
            description=_(u"""
                A i18n language definition string offerd in the skin for the 
                user to select.""")),
        required=False,
        )


class IOfferedLanguages(zope.interface.Interface):

    def getOfferedLanguages():
        """View for listing  available (offered) languages."""

    def hasOfferedLanguages():
        """View for to check if we have i18n session support."""


class IAvailableTranslationDomainLanguagesVocabulary(IVocabularyTokenized):
    """Available languages."""
