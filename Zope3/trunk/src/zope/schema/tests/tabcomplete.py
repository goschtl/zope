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

"""Example vocabulary for tab completion."""


from zope.schema.interfaces import ITerm, IVocabulary
from zope.interface import implements


class Term:
    implements(ITerm)

    def __init__(self, value):
        self.value = value


class TermIterator:
    def __init__(self, values):
        self._next = iter(values).next

    def __iter__(self):
        return self

    def next(self):
        return Term(self._next())


class CompletionVocabulary(object):
    implements(IVocabulary)

    def __init__(self, values):
        # In practice, something more dynamic could be used to
        # get the list possible completions.
        self._values = tuple(values)

    def __contains__(self, value):
        return value in self._values

    def getTerm(self, value):
        if value in self._values:
            return Term(value)
        raise LookupError(value)

    def __iter__(self):
        return TermIterator(self._values)

    def __len__(self):
        return len(self._values)

    def queryForPrefix(self, prefix):
        L = [v for v in self._values if v.startswith(prefix)]
        if L:
            return CompletionVocabulary(L)
        else:
            raise LookupError("no entries matching prefix %r" % prefix)
