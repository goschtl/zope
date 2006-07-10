##############################################################################
#
# Copyright (c) 2005, 2006 Zope Corporation and Contributors.
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

import time
from datetime import date

from zope.interface import implements
from zope.schema import Date
from zope.schema.interfaces import IFromUnicode

from zope.generic.field import IToUnicode



class EuroDate(Date):
    """DD.MM.YYYY Date."""

    implements(IFromUnicode, IToUnicode)

    def fromUnicode(self, str):
        """Retrieve a date from a unicode string.
        
        >>> field = EuroDate()
        >>> field.fromUnicode('12.3.2006')
        datetime.date(2006, 3, 12)
        
        >>> field.fromUnicode('12.33.2006')
        Traceback (most recent call last):
        ...
        ValueError: time data did not match format:  data=12.33.2006  fmt=%d.%m.%Y

        """
        
        timestamp = time.mktime(time.strptime(str, '%d.%m.%Y'))
        d = date.fromtimestamp(timestamp)

        self.validate(d)
        return d

    def toUnicode(self, value):
        """Retrieve a date from a unicode string.
        
        >>> field = EuroDate()
        >>> d = date(2006, 3, 12)
        >>> field.toUnicode(d)
        u'12.03.2006'

        """
        if value is None:
            return u''
        else:
            return unicode(value.strftime('%d.%m.%Y'))
        