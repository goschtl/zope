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

from zope.app.demo.widget.interfaces import IDemoTextWidget
from zope.app.demo.widget.app import DemoWidget


class DemoTextWidget(DemoWidget):
    """Demo TextLineWidget implementation.

    >>> content = DemoTextWidget()
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

    implements(IDemoTextWidget)

    standard = FieldProperty(IDemoTextWidget['standard'])
    required = FieldProperty(IDemoTextWidget['required'])
    readonly = FieldProperty(IDemoTextWidget['readonly'])
    constraint = FieldProperty(IDemoTextWidget['constraint'])
    default = FieldProperty(IDemoTextWidget['default'])
    min_length = FieldProperty(IDemoTextWidget['min_length'])
    max_length = FieldProperty(IDemoTextWidget['max_length'])
    min_max = FieldProperty(IDemoTextWidget['min_max'])
