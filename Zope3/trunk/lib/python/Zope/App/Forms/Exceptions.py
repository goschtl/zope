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

$Id: Exceptions.py,v 1.5 2002/11/30 18:32:58 jim Exp $
"""


class WidgetInputError(Exception):
    """There were one or more user input errors
    """

    def __init__(self, widget_name, widget_title, errors):
        Exception.__init__(self, widget_name, widget_title, errors)
        self.widget_name = widget_name
        self.widget_title = widget_title
        self.errors = errors

class MissingInputError(WidgetInputError):
    """Required data was not supplied
    """

class ConversionError(WidgetInputError):
    """If some conversion fails, this exception is raised.
    """

    def __init__(self, error_name, original_exception=None):
        Exception.__init__(self, error_name, original_exception)
        self.error_name = error_name
        self.original_exception = original_exception


class ErrorContainer(Exception):
    """A base error class for collecting multiple errors
    """

    def append(self, error):
        self.args += (error, )

    def __len__(self):
        return len(self.args)

    def __iter__(self):
        return iter(self.args)

    def __getitem__(self, i):
        return self.args[i]

    def __str__(self):
        return "\n".join(
            ["%s: %s" % (error.__class__.__name__, error)
             for error in self.args]
            )

    __repr__ = __str__

class WidgetsError(ErrorContainer):
    """A collection of errors from widget processing.
    """
