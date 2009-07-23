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
"""Spreadsheet Content

$Id$
"""
__docformat__ = "reStructuredText"
import zope.interface
import zope.schema
from zope.app.container import contained
from zope.schema.fieldproperty import FieldProperty


class ICandidate(zope.interface.Interface):

    lastName = zope.schema.TextLine(
        title=u'Last Name',
        description=u'The last name of the person.',
        default=u'',
        missing_value=u'',
        required=True)

    firstName = zope.schema.TextLine(
        title=u'First Name',
        description=u'The first name of the person.',
        default=u'',
        missing_value=u'',
        required=True)

    rating = zope.schema.Choice(
        title=u'Rating',
        description=u'The rating of the candidate.',
        values=[u'excellent', u'good', u'average', u'poor'],
        required=False)


class Candidate(contained.Contained):
    zope.interface.implements(ICandidate)

    lastName = FieldProperty(ICandidate['lastName'])
    firstName = FieldProperty(ICandidate['firstName'])
    rating = FieldProperty(ICandidate['rating'])

    def __init__(self, lastName, firstName, rating=None):
        self.lastName = lastName
        self.firstName = firstName
        self.rating = rating
