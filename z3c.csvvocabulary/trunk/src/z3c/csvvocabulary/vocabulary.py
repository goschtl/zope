##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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
"""CSV Vocabulary Implementation

$Id$
"""
__docformat__ = "reStructuredText"
import csv
import os.path

from zope.schema import vocabulary
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('zope')


def CSVVocabulary(filename, messageFactory=_):
    # Create a prefix
    prefix = os.path.split(filename)[-1][:-4]
    # Open a file and read the data
    f = file(filename)
    reader = csv.reader(f, delimiter=";")
    # Create the terms and the vocabulary
    terms = []
    for id, title in reader:
        title = unicode(title, 'latin1')
        term = vocabulary.SimpleTerm(
            id, title=messageFactory(prefix+'-'+id, default=title))
        terms.append(term)
    return vocabulary.SimpleVocabulary(terms)
