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

$Id: Exceptions.py,v 1.2 2002/10/09 13:53:54 mgedmin Exp $
"""


class WidgetInputError(Exception):
    """There were one or more user input errors
    """

    def __init__(self, widget_name, widget_title, errors):
        Exception.__init__(self, widget_name, widget_title, errors)
        self.widget_name = widget_name
        self.widget_title = widget_title
        self.errors = errors


class ConversionError(WidgetInputError):
    """If some conversion fails, this exception is raised.
    """

    def __init__(self, error_name, original_exception=None):
        Exception.__init__(self, error_name, original_exception)
        self.error_name = error_name
        self.original_exception = original_exception

