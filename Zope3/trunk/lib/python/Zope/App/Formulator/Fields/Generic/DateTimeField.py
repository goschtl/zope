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

$Id: DateTimeField.py,v 1.3 2002/07/17 23:11:32 jeremy Exp $
"""

from Zope.App.Formulator.Field import Field
from Zope.App.Formulator.Validators import DateTimeValidator 
from Zope.App.Formulator.Fields.Generic.IntegerField import IntegerField
from Zope.App.Formulator.Fields.Generic.ListField import ListField
from Zope.App.Formulator.Fields.Generic.MethodField import BoundMethod

import time


class DateTimeField(Field):

    __implements__ = Field.__implements__

    id = None
    default = ''
    title = 'DateTime Field'
    description = 'DateTime Field'
    validator = DateTimeValidator.DateTimeValidator()

            
    def on_value_input_style_changed(self, value):
        if value == 'text':
            self.sub_form = create_datetime_text_sub_form()
        elif value == 'list':
            self.sub_form = create_datetime_list_sub_form()
            year_field = self.sub_form.get_field('year')
            year_field.overrides['items'] = BoundMethod(self,
                                                        'override_year_items')
        else:
            assert 0, "Unknown input_style."
    
    def override_year_items(self):
        """The method gets called to get the right amount of years.
        """
        start_datetime = self.get_value('start_datetime')
        end_datetime = self.get_value('end_datetime')
        current_year = time.gmtime(time.time())[0]
        if start_datetime:
            first_year = start_datetime.year()
        else:
            first_year = current_year
        if end_datetime:
            last_year = end_datetime.year() + 1
        else:
            last_year = first_year + 11
        return create_items(first_year, last_year, digits=4)

            
def create_datetime_text_sub_form():
    sub_form = BasicForm()
        
    year = IntegerField('year',
                        title="Year",
                        required=0,
                        display_width=4,
                        display_maxwidth=4,
                        max_length=4)
    
    month = IntegerField('month',
                         title="Month",
                         required=0,
                         display_width=2,
                         display_maxwidth=2,
                         max_length=2)
    
    day = IntegerField('day',
                       title="Day",
                       required=0,
                       display_width=2,
                       display_maxwidth=2,
                       max_length=2)
    
    sub_form.add_group("date")
    sub_form.add_fields([year, month, day], "date")
    
    hour = IntegerField('hour',
                        title="Hour",
                        required=0,
                        display_width=2,
                        display_maxwidth=2,
                        max_length=2)
    
    minute = IntegerField('minute',
                          title="Minute",
                          required=0,
                          display_width=2,
                          display_maxwidth=2,
                          max_length=2)

    sub_form.add_group("time")
    sub_form.add_fields([hour, minute], "time")
    return sub_form


def create_datetime_list_sub_form():
    sub_form = BasicForm()

    year = ListField('year',
                     title="Year",
                     required=0,
                     default="",
                     items=create_items(2000, 2010, digits=4),
                     size=1)
    
    month = ListField('month',
                      title="Month",
                      required=0,
                      default="",
                      items=create_items(1, 13, digits=2),
                      size=1)
    
    day = ListField('day',
                    title="Day",
                    required=0,
                    default="",
                    items=create_items(1, 32, digits=2),
                    size=1)

    sub_form.add_group("date")
    sub_form.add_fields([year, month, day], "date")
    
    hour = IntegerField('hour',
                        title="Hour",
                        required=0,
                        display_width=2,
                        display_maxwidth=2,
                        max_length=2)
    
    minute = IntegerField('minute',
                          title="Minute",
                          required=0,
                          display_width=2,
                          display_maxwidth=2,
                          max_length=2)

    sub_form.add_group("time")
    sub_form.add_fields([hour, minute], "time")
    return sub_form

def create_items(start, end, digits=0):
    result = [("-", "")]
    if digits:
        format_string = "%0" + str(digits) + "d"
    else:
        format_string = "%s"
        
    for i in range(start, end):
        s = format_string % i
        result.append((s, s))
    return result
