##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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
"""Patched form converters for z3c.form 1.9

This module contains patched versions of z3c.form sequence converters
that fix an exception raised when the passed value is no more in terms.

This is already fixed in current z3c.form trunk (2.0+), so if you use
2.0, you don't need these converters.

$Id$
"""
from z3c.form import converter


class SequenceDataConverter(converter.SequenceDataConverter):

    def toWidgetValue(self, value):
        if value is self.field.missing_value:
            return []
        terms = self.widget.updateTerms()
        try:
            return [terms.getTerm(value).token]
        except LookupError, err:
            return []


class CollectionSequenceDataConverter(converter.CollectionSequenceDataConverter):

    def toWidgetValue(self, value):
        if value is self.field.missing_value:
            return []
        terms = self.widget.updateTerms()
        values = []
        for entry in value:
            try:
                values.append(terms.getTerm(entry).token)
            except LookupError, err:
                pass
        return values
