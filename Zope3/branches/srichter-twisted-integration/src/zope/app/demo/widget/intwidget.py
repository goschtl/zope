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

from zope.app.demo.widget.interfaces import IDemoIntWidget
from zope.app.demo.widget.app import DemoWidget


class DemoIntWidget(DemoWidget):
    """Demo TextWidget implementation.
    
    >>> content = DemoIntWidget()
    >>> content.standard

    >>> content.required = 42
    >>> content.required
    42

    >>> content.readonly = 42
    >>> content.readonly
    42

    >>> content.default
    42

    >>> content.standard

    >>> content.required = 42
    >>> content.required
    42

    >>> content.constraint = 42
    >>> content.constraint
    42

    >>> content.min = 6
    >>> content.min
    6

    >>> content.max = 1
    >>> content.max
    1

    >>> content.min_max = 6
    >>> content.min_max
    6
    
    """

    implements(IDemoIntWidget)
    
    standard = FieldProperty(IDemoIntWidget['standard'])
    required = FieldProperty(IDemoIntWidget['required'])
    readonly = FieldProperty(IDemoIntWidget['readonly'])
    constraint = FieldProperty(IDemoIntWidget['constraint'])
    default = FieldProperty(IDemoIntWidget['default'])
    min = FieldProperty(IDemoIntWidget['min'])
    max = FieldProperty(IDemoIntWidget['max'])
    min_max = FieldProperty(IDemoIntWidget['min_max'])