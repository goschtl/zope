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

$Id: SelectionValidator.py,v 1.2 2002/06/10 23:27:48 jim Exp $
"""

from StringBaseValidator import StringBaseValidator


class SelectionValidator(StringBaseValidator):

    __implements__ = StringBaseValidator.__implements__

    messageNames = StringBaseValidator.messageNames +\
                   ['unknownSelection']

    unknownSelection = 'You selected an item that was not in the list.'
    
    def validate(self, field, value):
        value = StringBaseValidator.validate(self, field, value)

        if value == "" and not field.get_value('required'):
            return value

        # get the text and the value from the list of items
        for item in field.get_value('items'):
            try:
                item_text, item_value = item
            except ValueError:
                item_text = item
                item_value = item
            
            # check if the value is equal to the *string* version of
            # item_value; if that's the case, we can return the *original*
            # value in the list (not the submitted value). This way, integers
            # will remain integers.
            if str(item_value) == value:
                return item_value
            
        # if we didn't find the value, return error
        self.raise_error('unknownSelection', field)
