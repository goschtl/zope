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
""" Skin Data metaclass

$Id$
"""
import sys
from zope.schema import getFields
from persistent import Persistent
from zope.app.container.contained import Contained
from zope.schema.fieldproperty import FieldProperty

from interfaces import _
from z3ext.controlpanel.storage import ConfigletData
from z3ext.controlpanel.configlettype import DataProperty

from interfaces import _

_marker = object()


class SkinDataType(type):
    """ Metaclass for skin data """

    def __new__(cls, name, schema, class_=None, *args, **kw):
        cname = 'SkinData<%s>'%name
        if type(class_) is tuple:
            bases = class_ + (Persistent, Contained,)
        elif class_ is not None:
            bases = (class_, Persistent, Contained)
        else:
            bases = (Persistent, Contained,)

        tp = type.__new__(cls, str(cname), bases, {})
        setattr(sys.modules['z3ext.skintool.skindatatype'], cname, tp)

        return tp

    def __init__(cls, name, schema, class_=None, title='', description=''):
        for f_id in getFields(schema):
            if not hasattr(cls, f_id):
                setattr(cls, f_id, FieldProperty(schema[f_id]))

        cls.__id__ = unicode(name)
        cls.__title__ = title
        cls.__description__ = description
        cls.__schema__ = DataProperty(schema)
