##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
$Id: FieldProperty.py,v 1.1 2002/09/07 16:18:51 jim Exp $
"""

__metaclass__ = type

_marker = object()

class FieldProperty:
    """Computed attributes based on schema fields

    Field properties provide default values, data validation and error messages
    based on data found in field meta-data.
    """

    def __init__(self, field, name=None):
        if name is None:
            name = field.__name__

        self.__field = field
        self.__name = name
        self.__private_name = "_fp__" + name

    def __get__(self, inst, klass):
        if inst is None:
            return self

        value = getattr(inst, self.__private_name, _marker)
        if value is _marker:
            value = getattr(self.__field, 'default', _marker)
            if value is _marker:
                raise AttributeError, self.__name

        return value

    def __set__(self, inst, value):
        self.__field.validate(value)
        setattr(inst, self.__private_name, value)
            

__doc__ = FieldProperty.__doc__ + __doc__

