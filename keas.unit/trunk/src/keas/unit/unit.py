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
"""Implementation of a unit converter

$Id$
"""
__docformat__ = "reStructuredText"
import decimal
import popen2
import zope.interface
from zope.schema.fieldproperty import FieldProperty
from keas.unit import interfaces

# set up internationalization
import zope.i18nmessageid
_ = zope.i18nmessageid.MessageFactory("keas.com")

class UnitConverter(object):
    zope.interface.implements(interfaces.IUnitConverter)

    executable = FieldProperty(interfaces.IUnitConverter['executable'])
    format = FieldProperty(interfaces.IUnitConverter['format'])
    filenames = FieldProperty(interfaces.IUnitConverter['filenames'])
    minusAsProduct = FieldProperty(interfaces.IUnitConverter['minusAsProduct'])

    def convert(self, fromUnit, toUnit):
        """See interfaces.IUnitConverter"""
        # Build the command
        cmd = self.executable + ' -t'
        if self.format:
            cmd += ' -o ' + self.format
        if self.filenames:
            cmd += ' -f ' + ' -f '.join([repr(fn) for fn in self.filenames])
        if self.minusAsProduct:
            cmd += ' ' + '-p'
        cmd += ' "' + fromUnit + '" "' + toUnit + '"'
        # Run the command
        stdout, stdin, stderr = popen2.popen3(cmd)
        result = stdout.read()
        try:
            return decimal.Decimal(result)
        except decimal.InvalidOperation, err:
            errorMessage = result
            if not errorMessage:
                errorMessage = stderr.read()
            errorMessage = errorMessage.split('\n')[0]
            raise interfaces.UnitConversionError(cmd, errorMessage)
