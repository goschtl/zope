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
"""IBAN Field interfaces

$Id: interfaces.py 77083 2007-06-25 22:56:42Z hermann $
"""
__docformat__ = "reStructuredText"
import zope.schema
from zope.schema import interfaces

from z3c.iban.i18n import MessageFactory as _

class IIBAN(interfaces.IField):
   """IBAN Field"""
