##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
"""Interfaces for a unit converter

$Id$
"""
__docformat__ = "reStructuredText"
import zope.interface
import zope.schema

# set up internationalization
import zope.i18nmessageid
_ = zope.i18nmessageid.MessageFactory("keas.com")

class IUnitConversionError(zope.interface.Interface):
    """An error raised when the unit conversion failed."""

class UnitConversionError(ValueError):
    zope.interface.implements(IUnitConversionError)


class IUnitConverter(zope.interface.Interface):
    """Component to provide the conversion factor of one unit to another."""

    executable = zope.schema.ASCIILine(
        title = u'Units executable',
        description = u'The path to the executable `units` script.',
        default = '/usr/bin/units')

    format = zope.schema.ASCIILine(
        title = u'Output format',
        description = u'The format used to produce the output.',
        required = False)

    filenames = zope.schema.Tuple(
        title = u'Data Files',
        description = u'A list of data files to use for the conversions.',
        required = False)

    minusAsProduct = zope.schema.Bool(
        title = u'Minus as Product',
        description = u'The minus character acts as a product operator.',
        default = False)

    def convert(fromUnit, toUnit):
        """Convert from one unit to another.

        Returns a decimal representing the conversion factor from one unit
        to another.

        If an error occurs, a `UnitConversionError` error is rasied.
        """
