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
"""Validation Exceptions

$Id: Exceptions.py,v 1.3 2002/09/11 22:06:41 jim Exp $
"""

class StopValidation(Exception):
    """This exception is raised, if the validation is done for sure early.
    Note that this exception should be always caught, since it is just a
    way for the validator to save time."""
    pass


class ValidationError(Exception):
    """If some check during the Validation process fails, this exception is
    raised."""

    def __cmp__(self, other):
        return cmp(self.args, other.args)

    def __repr__(self):
        return ' '.join(map(str, self.args))

# XXX YAGNI, this is doomed. ;)

class ErrorContainer(Exception):
    """ """

    def __init__(self, errors):
        Exception.__init__(self)
        self.errors = errors

    def __len__(self):
        return len(self.errors)

    def __getitem__(self, key):
        return self.errors[key]

    def __iter__(self):
        return iter(self.errors)


class ValidationErrorsAll(ErrorContainer):
    """This is a collection error that contains all exceptions that occured
    during the validation process."""


class ConversionErrorsAll(ErrorContainer):
    """This is a collection error that contains all exceptions that occured
    during the conversion process."""

