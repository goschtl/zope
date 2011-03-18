#############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
from zope import i18n
from zc.i18n.i18n import _

ONE_DAY = _('${number} day ${additional}')
MULTIPLE_DAYS = _('${number} days ${additional}')

ONE_HOUR = _('${number} hour ${additional}')
MULTIPLE_HOURS = _('${number} hours ${additional}')

ONE_MINUTE = _('${number} minute ${additional}')
MULTIPLE_MINUTES = _('${number} minutes ${additional}')

ONE_SECOND = _('${number} second')
MULTIPLE_SECONDS = _('${number} seconds')

NO_TIME = _('No time')

def format(request, duration):
    # this could be better, and better internationalized, but it is a start.
    # ICU does
    # not appear to support internationalizing durations over a day, at least
    # as found in
    # http://icu.sourceforge.net/apiref/icu4c/classRuleBasedNumberFormat.html
    # and related docs.
    # The approach here is to do what English needs in a reasonably flexible,
    # way and hope others tell us if we need to do more.
    if (duration.days > 0
        or duration.days < -1
        or duration.days == -1 and not duration.seconds):
        
        if duration.days > 0 or not duration.seconds:
            big = duration.days
            little = duration.seconds // 3600
        else: # negative and seconds
            big = duration.days + 1
            seconds = duration.seconds - 86400
            abs_seconds = abs(seconds)
            sign = seconds/abs_seconds
            little = (abs_seconds // 3600) * sign
        main = (MULTIPLE_DAYS, ONE_DAY)
        additional = (MULTIPLE_HOURS, ONE_HOUR)
    elif duration.days or duration.seconds:
        if duration.days == -1:
            seconds = duration.seconds - 86400
        else:
            seconds = duration.seconds
        abs_seconds = abs(seconds)
        sign = seconds/abs_seconds
        if abs_seconds // 3600:
            big = (abs_seconds // 3600) * sign
            little = ((abs_seconds % 3600) // 60) * sign
            main = (MULTIPLE_HOURS, ONE_HOUR)
            additional = (MULTIPLE_MINUTES, ONE_MINUTE)
        elif abs_seconds // 60:
            big = (abs_seconds // 60) * sign
            little = (abs_seconds % 60) * sign
            main = (MULTIPLE_MINUTES, ONE_MINUTE)
            additional = (MULTIPLE_SECONDS, ONE_SECOND)
        else:
            big = seconds
            little = None
            main = (MULTIPLE_SECONDS, ONE_SECOND)
    else:
        return i18n.translate(NO_TIME, context=request)
    if little:
        message = additional[abs(little)==1]
        additional = i18n.translate(
            i18n.Message(
                message,
                mapping={'number': str(little), 'additional': ''}),
            context=request)
    else:
        additional = ''
    message = main[abs(big)==1]
    return i18n.translate(
        i18n.Message(
            message,
            mapping={'number': str(big), 'additional': additional}),
        context=request)
