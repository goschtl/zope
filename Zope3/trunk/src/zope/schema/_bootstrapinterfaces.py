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
"""Bootstrap schema interfaces and exceptions

$Id: _bootstrapinterfaces.py,v 1.1 2003/10/15 20:28:22 shane Exp $
"""
from zope.interface import Interface


class StopValidation(Exception):
    """Raised if the validation is completed early.

    Note that this exception should be always caught, since it is just
    a way for the validator to save time.
    """


class ValidationError(Exception):
    """Raised if the Validation process fails."""

    def __cmp__(self, other):
        return cmp(self.args, other.args)

    def __repr__(self):
        return ' '.join(map(str, self.args))

class IFromUnicode(Interface):
    """Parse a unicode string to a value

    We will often adapt fields to this interface to support views and
    other applications that need to conver raw data as unicode
    values.

    """

    def fromUnicode(str):
        """Convert a unicode string to a value.
        """
