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
"""Sub-index factories for mult-field index

$Id$
"""
from zc.catalog.index import ValueIndex, SetIndex
from zope.component import adapts
from zope.index.text import TextIndex
from zope.interface import implements
from zope.schema.interfaces import IField, ICollection, IText

from z3c.multifieldindex.interfaces import ISubIndexFactory


class SubIndexFactoryBase(object):
    implements(ISubIndexFactory)
    
    factory = None
    
    def __init__(self, field):
        self.field = field
        
    def __call__(self):
        return self.factory()


class DefaultIndexFactory(SubIndexFactoryBase):
    adapts(IField)
    factory = ValueIndex


class CollectionIndexFactory(SubIndexFactoryBase):
    adapts(ICollection)
    factory = SetIndex


class TextIndexFactory(SubIndexFactoryBase):
    adapts(IText)
    factory = TextIndex
