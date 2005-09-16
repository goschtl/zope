##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Item Vocabulary

Given a context object that implements `IEnumerableMapping`, the vocabulary
displays all items of that context object. 

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.interface import implements
from zope.schema.interfaces import ITokenizedTerm, IVocabularyTokenized
from zope.interface.common.mapping import IEnumerableMapping


class ItemTerm(object):
    """A simple term implementation for items."""
    implements(ITokenizedTerm)
    def __init__(self, value):
        self.value = self.token = value


class ItemVocabulary(object):
    """A vocabulary that provides the keys of any `IEnumerableMapping` object.

    Every dictionary will qualify for this vocabulary.

    Example::

      >>> data = {'a': 'Anton', 'b': 'Berta', 'c': 'Charlie'}
      >>> vocab = ItemVocabulary(data)
      >>> iterator = iter(vocab)
      >>> iterator.next().token
      'a'
      >>> len(vocab)
      3
      >>> 'c' in vocab
      True
      >>> vocab.getTerm('b').value
      'b'
      >>> vocab.getTerm('d')
      Traceback (most recent call last):
      ...
      LookupError: d
      >>> vocab.getTermByToken('b').token
      'b'
      >>> vocab.getTermByToken('d')
      Traceback (most recent call last):
      ...
      LookupError: d
    """
    implements(IVocabularyTokenized)
    __used_for__ = IEnumerableMapping

    def __init__(self, context):
        self.context = context
    
    def __iter__(self):
        """See zope.schema.interfaces.IIterableVocabulary"""
        return iter([ItemTerm(key) for key in self.context.keys()])
    
    def __len__(self):
        """See zope.schema.interfaces.IIterableVocabulary"""
        return len(self.context)
    
    def __contains__(self, value):
        """See zope.schema.interfaces.IBaseVocabulary"""
        return value in self.context.keys()

    def getTerm(self, value):
        """See zope.schema.interfaces.IBaseVocabulary"""
        if value not in self.context.keys():
            raise LookupError, value
        return ItemTerm(value)

    def getTermByToken(self, token):
        """See zope.schema.interfaces.IVocabularyTokenized"""
        return self.getTerm(token)
