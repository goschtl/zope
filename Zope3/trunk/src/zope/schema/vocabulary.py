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

"""Vocabulary support for schema."""

from zope.schema import Field
from zope.schema import errornames
from zope.schema.interfaces import ValidationError
from zope.schema.interfaces import IVocabularyRegistry
from zope.schema.interfaces import IVocabularyField, IVocabularyMultiField

try:
    basestring  # new in Python 2.3
except NameError:
    from types import StringTypes as basestring


class VocabularyField(Field):
    """Field that adds support for use of an external vocabulary.

    The value is a single value from the vocabulary.
    """
    __implements__ = IVocabularyField

    def __init__(self, vocabulary=None, **kw):
        # set up the vocabulary:
        if isinstance(vocabulary, basestring):
            self.vocabulary = None
            self.vocabularyName = vocabulary
        else:
            assert vocabulary is not None
            self.vocabulary = vocabulary
            self.vocabularyName = None
        # call the base initializer
        super(VocabularyField, self).__init__(**kw)

    def _validate(self, value):
        if self.vocabulary is None:
            if self.context is not None:
                raise ValueError("can't validate value without vocabulary")
            # XXX can't validate without vocabulary, and can't get
            # vocabulary without context
            return
        if value not in self.vocabulary:
            raise ValidationError(errornames.ConstraintNotSatisfied,
                                  value)

    def bind(self, object):
        clone = super(VocabularyField, self).bind(object)
        # get registered vocabulary/presentation if needed:
        if clone.vocabulary is None:
            vr = getVocabularyRegistry()
            clone.vocabulary = vr.get(object, self.vocabularyName)
        return clone


class VocabularyMultiField(VocabularyField):
    """Field that adds support for use of an external vocabulary.

    The value is a collection of values from the vocabulary.
    """
    __implements__ = IVocabularyMultiField

    def _validate(self, value):
        vocab = self.vocabulary
        if vocab is None:
            raise ValueError("can't validate value without vocabulary")
        for v in value:
            if v not in vocab:
                raise ValidationError(errornames.ConstraintNotSatisfied, v)


class VocabularyRegistryError(LookupError):
    def __init__(self, name):
        self.name = name
        Exception.__init__(self, str(self))

    def __str__(self):
        return "unknown vocabulary: %r" % self.name


class VocabularyRegistry(object):
    __slots__ = '_map',
    __implements__ = IVocabularyRegistry

    def __init__(self):
        self._map = {}

    def get(self, object, name):
        try:
            vtype = self._map[name]
        except KeyError:
            raise VocabularyRegistryError(name)
        return vtype(object)

    def register(self, name, factory):
        self._map[name] = factory


_vocabularies = None

def getVocabularyRegistry():
    """Return the vocabulary registry.

    If the registry has not been created yet, an instance of
    VocabularyRegistry will be installed and used.
    """
    if _vocabularies is None:
        setVocabularyRegistry(VocabularyRegistry())
    return _vocabularies

def setVocabularyRegistry(registry):
    """Set the vocabulary registry."""
    global _vocabularies
    if _vocabularies is not None:
        raise ValueError("vocabulary registry has already been set")
    _vocabularies = registry

def _clear():
    """Remove the registries (for use by tests)."""
    global _vocabularies
    _vocabularies = None


try:
    from zope.testing.cleanup import addCleanUp
except ImportError:
    # don't have that part of Zope
    pass
else:
    addCleanUp(_clear)
    del addCleanUp
