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
"""Common Schema Error Names

$Id: errornames.py,v 1.3 2003/07/14 15:28:35 Zen Exp $

Defines common validation error messages.
Using these symbols instead of strings makes unit tests less fragile,
as the strings are only defined in one place. Otherwise, this module
serves no real function.
"""
from zope.app.i18n import ZopeMessageIDFactory as _

WrongType = _(u'Wrong type')

RequiredMissing = _(u'Input is required') # Required input missing

RequiredEmptyStr = _(u'Required empty string')

TooBig = _(u'Too big')

TooSmall = _(u'Too small')

TooLong = _(u'Too long')

TooShort = _(u'Too short')

InvalidValue = _(u'Invalid value')

TooManyDecimals = _(u'Too many decimals')

WrongContainedType = _(u"Wrong contained type")

ConstraintNotSatisfied = _(u'Constraint not satisfied')

NotAContainer = _(u'Not a container')

NotAnIterator = _(u'Not an iterator')
