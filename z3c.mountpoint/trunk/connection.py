##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
"""A simple multi-database mount-point implementation

$Id$
"""
__docformat__ = "reStructuredText"
from zope.schema import vocabulary
from zope.app.component import hooks

def ZODBConnectionNamesVocabulary(context):
    return vocabulary.SimpleVocabulary(
        [vocabulary.SimpleTerm(name)
         for name in hooks.getSite()._p_jar.db().databases])
