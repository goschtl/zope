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

import copy

from zope.interface.declarations import directlyProvides, implements
from zope.schema import errornames
from zope.schema import Field
from zope.schema import MinMaxLen
from zope.schema._bootstrapfields import ValidatedProperty
from zope.schema.interfaces import ValidationError
from zope.schema.interfaces import IVocabularyRegistry
from zope.schema.interfaces import IVocabularyField
from zope.schema.interfaces import IVocabularyBagField, IVocabularyListField
from zope.schema.interfaces import IVocabularySetField
from zope.schema.interfaces import IVocabularyUniqueListField
from zope.schema.interfaces import IVocabulary, IVocabularyTokenized
from zope.schema.interfaces import ITokenizedTerm

class ContainerValidatedProperty(ValidatedProperty):

    def __get__(self, inst, type=None):
        name, check = self._info
        try:
            value = inst.__dict__[name]
        except KeyError:
            raise AttributeError, name
        if value is not None:
            value = copy.copy(value)
        return value


class BaseVocabularyField(Field):


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
        super(BaseVocabularyField, self).__init__(**kw)

    def bind(self, object):
        clone = super(BaseVocabularyField, self).bind(object)
        # get registered vocabulary/presentation if needed:
        if clone.vocabulary is None:
            vr = getVocabularyRegistry()
            clone.vocabulary = vr.get(object, self.vocabularyName)
        return clone


class VocabularyField(BaseVocabularyField):
    """Field that adds support for use of an external vocabulary.

    The value is a single value from the vocabulary.
    """
    implements(IVocabularyField)

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


class VocabularyMultiField(MinMaxLen, BaseVocabularyField):
    """Field that adds support for use of an external vocabulary.

    The value is a collection of values from the vocabulary.

    This class cannot be used directly; a subclass must be used to
    specify concrete behavior.
    """

    default = ContainerValidatedProperty("default")

    def __init__(self, **kw):
        if self.__class__ is VocabularyMultiField:
            raise NotImplementedError(
                "The VocabularyMultiField class cannot be used directly.")
        if "default" not in kw and not kw.get("min_length"):
            kw["default"] = []
        super(VocabularyMultiField, self).__init__(**kw)

    def _validate(self, value):
        vocab = self.vocabulary
        if value:
            if vocab is None:
                raise ValueError("can't validate value without vocabulary")
            for v in value:
                if v not in vocab:
                    raise ValidationError(errornames.ConstraintNotSatisfied, v)
        super(VocabularyMultiField, self)._validate(value)

class UniqueElements(object):
    """Mix-in class that checks that each contained element is unique."""

    def _validate(self, value):
        d = {}
        for v in value:
            if v in d:
                raise ValidationError()
            d[v] = v
        super(UniqueElements, self)._validate(value)

class VocabularyBagField(VocabularyMultiField):
    implements(IVocabularyBagField)
    __doc__ = IVocabularyBagField.__doc__

class VocabularyListField(VocabularyMultiField):
    implements(IVocabularyListField)
    __doc__ = IVocabularyListField.__doc__

class VocabularySetField(UniqueElements, VocabularyMultiField):
    implements(IVocabularySetField)
    __doc__ = IVocabularySetField.__doc__

class VocabularyUniqueListField(UniqueElements, VocabularyMultiField):
    implements(IVocabularyUniqueListField)
    __doc__ = IVocabularyUniqueListField.__doc__


# simple vocabularies performing enumerated-like tasks

class SimpleTerm:
    """Simple tokenized term used by SimpleVocabulary."""

    implements(ITokenizedTerm)

    def __init__(self, value, token=None):
        """Create a term for value and token. If token is omitted,
        str(value) is used for the token
        """
        self.value = value
        if token is None:
            token = value
        self.token = str(token)

class SimpleVocabulary(object):
    """Vocabulary that works from a sequence of terms."""

    implements(IVocabulary, IVocabularyTokenized)

    def __init__(self, terms, *interfaces):
        """Initialize the vocabulary given a list of terms.

        The vocabulary keeps a reference to the list of terms passed
        in; it should never be modified while the vocabulary is used.

        One or more interfaces may also be provided so that alternate
        widgets may be bound without subclassing.
        """
        self.by_value = {}
        self.by_token = {}
        self._terms = terms
        for term in self._terms:
            self.by_value[term.value] = term
            self.by_token[term.token] = term
        assert len(self.by_value) == len(self.by_token) == len(terms), \
               'Supplied vocabulary values resulted in duplicate term tokens'
        if interfaces:
            directlyProvides(self, *interfaces)

    def fromItems(cls, items, *interfaces):
        """Construct a vocabulary from a list of (token, value) pairs.

        The order of the items is preserved as the order of the terms
        in the vocabulary.  Terms are created by calling the class
        method createTerm() with the pair (value, token).

        One or more interfaces may also be provided so that alternate
        widgets may be bound without subclassing.
        """
        terms = [cls.createTerm((value, token)) for (token, value) in items]
        return cls(terms, *interfaces)
    fromItems = classmethod(fromItems)

    def fromValues(cls, values, *interfaces):
        """Construct a vocabulary from a simple list.

        Values of the list become both the tokens and values of the
        terms in the vocabulary.  The order of the values is preserved
        as the order of the terms in the vocabulary.  Tokens are
        created by calling the class method createTerm() with the
        value as the only parameter.

        One or more interfaces may also be provided so that alternate
        widgets may be bound without subclassing.
        """
        terms = [cls.createTerm(value) for value in values]
        return cls(terms, *interfaces)
    fromValues = classmethod(fromValues)

    def createTerm(cls, data):
        """Create a single term from data.

        Subclasses may override this with a class method that creates
        a term of the appropriate type from the single data argument.
        """
        if isinstance(data, tuple):
            return SimpleTerm(*data)
        else:
            return SimpleTerm(data)
    createTerm = classmethod(createTerm)

    def __contains__(self, value):
        return value in self.by_value

    def getQuery(self):
        return None

    def getTerm(self, value):
        try:
            return self.by_value[value]
        except KeyError:
            raise LookupError(value)

    def getTermByToken(self, token):
        try:
            return self.by_token[token]
        except KeyError:
            raise LookupError(token)

    def __iter__(self):
        return iter(self._terms)

    def __len__(self):
        return len(self.by_value)

# registry code

class VocabularyRegistryError(LookupError):
    def __init__(self, name):
        self.name = name
        Exception.__init__(self, str(self))

    def __str__(self):
        return "unknown vocabulary: %r" % self.name


class VocabularyRegistry(object):
    __slots__ = '_map',
    implements(IVocabularyRegistry)

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
