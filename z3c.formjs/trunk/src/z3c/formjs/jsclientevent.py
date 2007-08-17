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
"""Javascript Functions.

$Id: jsfunction.py 78862 2007-08-16 00:16:19Z srichter $
"""
__docformat__ = "reStructuredText"
import sys
import zope.component
import zope.interface

from z3c.formjs import interfaces, jsfunction

def listener(eventType):
    """A decorator for defining a javascript function that is a listener."""
    namespace = "%s_%s" % (eventType.__module__.replace(".","_"), eventType.__name__)
    return jsfunction.function(namespace)
