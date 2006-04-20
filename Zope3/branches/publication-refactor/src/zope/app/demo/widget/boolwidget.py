##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Demo widget implementation

$Id$
"""
__docformat__ = 'restructuredtext'

from persistent import Persistent
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty

from zope.app.demo.widget.interfaces import IDemoBoolWidget
from zope.app.demo.widget.app import DemoWidget


class DemoBoolWidget(DemoWidget):
    """Demo BoolWidget implementation.
    
    >>> content = DemoBoolWidget()
    >>> content.standard

    >>> content.required = True
    >>> content.required
    True

    >>> content.readonly = True
    >>> content.readonly
    True

    >>> content.default
    True

    >>> content.standard

    >>> content.required = True
    >>> content.required
    True

    >>> content.constraint = True
    >>> content.constraint
    True
    
    """

    implements(IDemoBoolWidget)
    
    standard = FieldProperty(IDemoBoolWidget['standard'])
    required = FieldProperty(IDemoBoolWidget['required'])
    readonly = FieldProperty(IDemoBoolWidget['readonly'])
    constraint = FieldProperty(IDemoBoolWidget['constraint'])
    default = FieldProperty(IDemoBoolWidget['default'])