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

$Id: DateTimeWidget.py,v 1.2 2002/06/10 23:27:49 jim Exp $
"""

from Zope.App.PageTemplate import ViewPageTemplateFile
from Widget import Widget
from DateTime import DateTime


class DateTimeWidget(CompositeWidget):


    __implements__ = CompositeWidget.__implements__
    

    propertyNames = Widget.property_names +\
                     ['dateSeparator', 'timeSeparator',
                      'inputStyle', 'inputOrder', 'dateOnly']

    template = ViewPageTemplateFile('datetime.pt')

    widgets = {'year': IntegerWidget(start=0, end=6000),
               'month': IntegerWidget(start=0, end=12),
               'day': IntegerWidget(start=0, end=31),
               'hour': IntegerWidget(start=0, end=23),
               'minute': IntegerWidget(start=0, end=59)}

    default = None
    defaultNow = 0                      
    dateSeparator = '/'
    timeSeparator = ':'
    inputStyle = "text"
    inputOrder = ('year', 'month', 'day')
    dateOnly = 0
