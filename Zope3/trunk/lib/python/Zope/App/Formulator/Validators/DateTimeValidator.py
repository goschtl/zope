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
"""

$Id: DateTimeValidator.py,v 1.2 2002/06/10 23:27:48 jim Exp $
"""

from StringValidator import StringValidator
from Zope.Misc.DateTimeParse import parse


class DateTimeValidator(StringValidator):

    propertyNames = StringValidator.propertyNames + \
                    ['required', 'startDateTime', 'endDateTime']

    requiredNotFound = 'Input is required but no input given.'
    notDateTime = 'You did not enter a valid date and time.'
    datetimeOutOfRange = 'The date and time you entered were out of range.'
    
    def validate(self, field, key, REQUEST):    
        try:
            year = field.validate_sub_field('year', REQUEST)
            month = field.validate_sub_field('month', REQUEST)
            day = field.validate_sub_field('day', REQUEST)
            
            if field.get_value('date_only'):
                hour = 0
                minute = 0
            else:
                hour = field.validate_sub_field('hour', REQUEST)
                minute = field.validate_sub_field('minute', REQUEST)
        except ValidationError:
            self.raiseError('not_datetime', field)

        # handling of completely empty sub fields
        if ((year == '' and month == '' and day == '') and
            (field.get_value('date_only') or (hour == '' and minute == ''))): 
            if field.get_value('required'):
                self.raise_error('required_not_found', field)
            else:
                # field is not required, return None for no entry
                return None
        # handling of partially empty sub fields; invalid datetime
        if ((year == '' or month == '' or day == '') or
            (not field.get_value('date_only') and
             (hour == '' or minute == ''))):
            self.raise_error('not_datetime', field)

        try:
            result = parse('%s/%s/%s %s:%s' %(year, month, day, hour, minute))
        # ugh, a host of string based exceptions
        except ('DateTimeError', 'Invalid Date Components', 'TimeError'):
            self.raise_error('not_datetime', field)

        # check if things are within range
        start_datetime = field.get_value('start_datetime')
        if (start_datetime is not None and
            result < start_datetime):
            self.raise_error('datetime_out_of_range', field)
        end_datetime = field.get_value('end_datetime')
        if (end_datetime is not None and
            result >= end_datetime):
            self.raise_error('datetime_out_of_range', field)

        return result
