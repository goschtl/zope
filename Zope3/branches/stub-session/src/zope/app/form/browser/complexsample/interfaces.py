##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Interfaces used with the sample widget.

$Id$
"""
from zope.schema import BytesLine
from zope.schema.interfaces import IVocabularyQuery
from zope.schema.interfaces import IVocabularyTokenized, IBaseVocabulary
from zope.schema.interfaces import ITokenizedTerm

from zope.app.form.browser.complexsample.widgetapi import _


class ITitledTokenizedTerm(ITokenizedTerm):
    """ITokenizedTerm that also has a title attribute."""

    title = BytesLine(title=_(u"Title"))


class ISampleVocabulary(IBaseVocabulary, IVocabularyTokenized):
    """Vocabulary representing sample values."""


class ISampleVocabularyQuery(IVocabularyQuery):
    def query(text):
        """Returns a subset sample vocabulary based on canned data."""


class IFancySampleVocabularyQuery(IVocabularyQuery):
    def query(text, type=None):
        """Returns a subset sample vocabulary based on canned data."""

    def getReferenceTypes():
        """Return a sequence of type values that can be passed to query()."""
