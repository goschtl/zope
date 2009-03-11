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
""" z3ext.formatter interfaces

$Id$
"""
import vocabulary
from zope import schema, interface
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('z3ext.formatter')


class FormatterNotDefined(Exception):
    """ """

class FormatterExpressionError(Exception):
    """ """


class IFormatterConfiglet(interface.Interface):

    timezone = schema.Choice(
        title = _(u'Timezone'),
        description = _(u'Portal timezone.'),
        default = 'US/Pacific',
        vocabulary = vocabulary.timezones,
        required = False)

    timezoneFormat = schema.Choice(
        title = _(u'Timezone format'),
        description = _(u'Timezone format'),
        default = 3,
        vocabulary = vocabulary.timezonesOptions,
        required = False)

    principalTimezone = schema.Bool(
        title = _(u'Use principal timezone'),
        description = _(u'Render datetime with user selected timezone.'),
        default = True,
        required = False)


class IFormatterFactory(interface.Interface):
    """ formatter factory """

    def __call__(*args):
        """ create formatter """


class IFormatter(interface.Interface):
    """ locale formatter """

    def format(value):
        """ format value """
