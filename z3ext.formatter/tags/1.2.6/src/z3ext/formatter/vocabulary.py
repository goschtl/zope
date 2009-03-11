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
""" vocabularies

$Id$
"""
import pytz
from zope import interface
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('z3ext.formatter')


timezonesOptions = SimpleVocabulary(
    [SimpleTerm(1, '1', _(u'No timezone')),
     SimpleTerm(2, '2', _(u'Number of hours')),
     SimpleTerm(3, '3', _(u'Timezone name'))])

timezones = SimpleVocabulary(
    [SimpleTerm(unicode(tz), tz, unicode(tz)) for tz in pytz.common_timezones])


class Timezones(object):
    interface.implements(IVocabularyFactory)

    def __call__(self, context):
        return timezones
