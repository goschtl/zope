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
"""Questionnaire Implementation

$Id$
"""
__docformat__ = "reStructuredText"
import persistent
import zope.interface
from zope.location import location
from zope.schema.fieldproperty import FieldProperty
from z3c.formdemo.questionnaire import interfaces

class Questionnaire(location.Location, persistent.Persistent):
    zope.interface.implements(interfaces.IQuestionnaire)

    name = FieldProperty(interfaces.IQuestionnaire['name'])
    age = FieldProperty(interfaces.IQuestionnaire['age'])
    zope2 = FieldProperty(interfaces.IQuestionnaire['zope2'])
    plone = FieldProperty(interfaces.IQuestionnaire['plone'])
    zope3 = FieldProperty(interfaces.IQuestionnaire['zope3'])
    five = FieldProperty(interfaces.IQuestionnaire['five'])
    contributor = FieldProperty(interfaces.IQuestionnaire['contributor'])
    years = FieldProperty(interfaces.IQuestionnaire['years'])
    zopeId = FieldProperty(interfaces.IQuestionnaire['zopeId'])

    def __init__(self, **kw):
        for name, value in kw.items():
            setattr(self, name, value)
