##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""Currency Field interfaces

$Id$
"""
__docformat__ = "reStructuredText"
import zope.schema
from zope.schema import interfaces

from z3c.currency.i18n import MessageFactory as _

# Precisions
DOLLARS = 0
CENTS = 1

class ICurrency(interfaces.IMinMax, interfaces.IField):

    precision = zope.schema.Int(
        title=_('Precision'),
        description=_('The precision in which the amount is kept.'),
        default=CENTS,
        required=True)

    unit = zope.schema.TextLine(
        title=_('Unit'),
        description=_('The unit in which the currency amount is kept.'),
        default=u'$',
        required=True)
