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

$Id: MultiSelectionValidator.py,v 1.2 2002/06/10 23:27:48 jim Exp $
"""

from Zope.App.Formulator.Validator import Validator
from types import ListType

class MultiSelectionValidator(Validator):
    """ """
    
    __implements__ = Validator.__implements__

    propertyNames = Validator.propertyNames + ['required']

    required = 1

    messageNames = Validator.messageNames + ['requiredNotFound',
                                             'unknownSelection']
    
    requiredNotFound = 'Input is required but no input given.'
    unknownSelection = 'You selected an item that was not in the list.'

    
    def validate(self, field, value):
        values = value
        # NOTE: a hack to deal with single item selections
        if not isinstance(values, ListType):
            # put whatever we got in a list
            values = [values]

        # if we selected nothing and entry is required, give error, otherwise
        # give entry list
        if len(values) == 0:
            if field.get_value('isRequired'):
                self.raise_error('requiredNotFound', field)
            else:
                return values
            
        # create a dictionary of possible values
        value_dict = {}
        for item in field.get_value('items'):
            try:
                item_text, item_value = item
            except ValueError:
                item_text = item
                item_value = item
            value_dict[item_value] = 0
        # check whether all values are in dictionary
        result = []
        for value in values:
            # FIXME: hack to accept int values as well
            try:
                int_value = int(value)
            except ValueError:
                int_value = None
            if int_value is not None and (int_value in value_dict):
                result.append(int_value)
                continue
            if value in value_dict:
                result.append(value)
                continue
            self.raise_error('unknownSelection', field)
        # everything checks out
        return result
