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
"""Questionnaire Interfaces

$Id$
"""
__docformat__ = "reStructuredText"
import zope.interface
import zope.schema

class IQuestionnaire(zope.interface.Interface):
    """A questionaire about Zope users."""

    name = zope.schema.TextLine(
        title=u'Name',
        description=u'Name of the person.',
        required=True)

    age = zope.schema.Int(
        title=u'Age',
        description=u'The age of the person.',
        required=True)

    zope2 = zope.schema.Bool(
        title=u'Zope 2',
        description=u'Have you ever developed with Zope 2?',
        required=True)

    plone = zope.schema.Bool(
        title=u'Plone',
        description=u'Have you ever developed with Plone?',
        required=True)

    zope3 = zope.schema.Bool(
        title=u'Zope 3',
        description=u'Have you ever developed with Zope 3?',
        required=True)

    five = zope.schema.Bool(
        title=u'Five',
        description=u'Have you ever developed with Five?',
        required=True)

    contributor = zope.schema.Bool(
        title=u'Contrib.',
        description=u'Are you a Zope contributor?',
        required=True)

    years = zope.schema.Int(
        title=u'Years',
        description=u'How many years have you contributed?',
        default=0,
        required=False)

    zopeId = zope.schema.TextLine(
        title=u'Zope Id',
        description=u'What is your Zope Id?',
        required=False)

