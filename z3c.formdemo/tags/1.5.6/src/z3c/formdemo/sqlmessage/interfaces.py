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
"""Hello World Message Interfaces

$Id$
"""
__docformat__ = "reStructuredText"
import os
import zope.interface
import zope.schema
from z3c.csvvocabulary import CSVVocabulary

WhatVocabulary = CSVVocabulary(
    os.path.join(os.path.dirname(__file__), 'what-values.csv'))

class IHelloWorld(zope.interface.Interface):
    """Information about a hello world message"""

    who = zope.schema.TextLine(
        title=u'Who',
        description=u'Name of the person sending the message',
        required=True)

    when = zope.schema.Date(
        title=u'When',
        description=u'Date of the message sent.',
        required=True)

    what = zope.schema.Choice(
        title=u'What',
        description=u'What type of message it is.',
        vocabulary=WhatVocabulary,
        default=u'cool',
        required=True)
