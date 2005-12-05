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

from zope.app.demo.widget.interfaces import IDemoTextAreaWidget
from zope.app.demo.widget.app import DemoWidget


class DemoTextAreaWidget(DemoWidget):
    """Demo TextAreaWidget implementation.
    
    >>> content = DemoTextAreaWidget()
    >>> content.standard

    >>> content.required = u''
    >>> content.required
    u''

    >>> content.readonly = u"Attention, the FieldProperty doesn't validate!"
    >>> content.readonly
    u"Attention, the FieldProperty doesn't validate!"

    >>> content.constraint = u'constraint'
    >>> content.constraint
    u'constraint'

    >>> content.min_length = u'aaaaaa'
    >>> content.min_length
    u'aaaaaa'

    >>> content.max_length = u'a'
    >>> content.max_length
    u'a'

    >>> content.min_max = u'aaaaaa'
    >>> content.min_max
    u'aaaaaa'
    
    """

    implements(IDemoTextAreaWidget)
    
    standard = FieldProperty(IDemoTextAreaWidget['standard'])
    required = FieldProperty(IDemoTextAreaWidget['required'])
    readonly = FieldProperty(IDemoTextAreaWidget['readonly'])
    constraint = FieldProperty(IDemoTextAreaWidget['constraint'])
    default = FieldProperty(IDemoTextAreaWidget['default'])
    min_length = FieldProperty(IDemoTextAreaWidget['min_length'])
    max_length = FieldProperty(IDemoTextAreaWidget['max_length'])
    min_max = FieldProperty(IDemoTextAreaWidget['min_max'])