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

$Id: Exceptions.py,v 1.4 2002/07/14 13:32:53 srichter Exp $
"""

class StopValidation(Exception):
    """This exception is raised, if the validation is done for sure early.
    Note that this exception should be always caught, since it is just a
    way for the validator to save time."""
    pass


class ValidationError(Exception):
    """If some check during the Validation process fails, this exception is
    raised."""

    def __init__(self, error_name):
        Exception.__init__(self)
        self.error_name = error_name

    def __cmp__(self, other):
        return cmp(self.error_name, other.error_name)


class ValidationErrorsAll(Exception):
    """This is a collection error that contains all exceptions that occured
    during the validation process."""

    def __init__(self, list):
        Exception.__init__(self)
        self.errors = list
