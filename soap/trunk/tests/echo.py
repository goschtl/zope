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
"""
Simple SOAP interop testing view.

$Id: $
"""

from soap.view import SOAPView

class Echo(SOAPView):
    """A test SOAP view."""

    def echoString(self, value):
        return value

    def echoStringArray(self, value):
        return value

    def echoInteger(self, value):
        return value

    def echoIntegerArray(self, value):
        return value

    def echoFloat(self, value):
        return value

    def echoFloatArray(self, value):
        return value

    def echoStruct(self, value):
        return value

    def echoStructArray(self, value):
        return value

    def echoVoid(self, value):
        return value

    def echoBase64(self, value):
        return value

    def echoHexBinary(self, value):
        return value

    def echoDate(self, value):
        return value

    def echoDecimal(self, value):
        return value

    def echoBoolean(self, value):
        return value

