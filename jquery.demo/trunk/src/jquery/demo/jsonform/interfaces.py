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
"""
$Id: layer.py 197 2007-04-13 05:03:32Z rineichen $
"""

import datetime
import decimal
import zope.interface
import zope.schema
from z3c.website import interfaces


class IJSONFormSample(interfaces.ISample):
    """JSON form sample."""


class IAnotherSessionData(zope.interface.Interface):
    """Simple data object which offers a field called content."""

    asciiField = zope.schema.ASCII(
        title=u'ASCII',
        description=u'This is an ASCII field.',
        default='This is\n ASCII.')

    asciiLineField = zope.schema.ASCIILine(
        title=u'ASCII Line',
        description=u'This is an ASCII-Line field.',
        default='An ASCII line.')

    dateField = zope.schema.Date(
        title=u'Date',
        description=u'This is a Date field.',
        default=datetime.date(2007, 4, 1))

    datetimeField = zope.schema.Datetime(
        title=u'Date/Time',
        description=u'This is a Datetime field.',
        default=datetime.datetime(2007, 4, 1, 12))

    decimalField = zope.schema.Decimal(
        title=u'Decimal',
        description=u'This is a Decimal field.',
        default=decimal.Decimal('12.87'))

    dottedNameField = zope.schema.DottedName(
        title=u'Dotted Name',
        description=u'This is a DottedName field.',
        default='z3c.form')

    floatField = zope.schema.Float(
        title=u'Float',
        description=u'This is a Float field.',
        default=12.8)

    idField = zope.schema.Id(
        title=u'Id',
        description=u'This is a Id field.',
        default='z3c.form')

