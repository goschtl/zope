##############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
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
"""Vocabulary support for schema.
"""
try:
    from collections import OrderedDict
except:
    from ordereddict import OrderedDict

from zope.interface.declarations import directlyProvides, implementer
from zope.schema.interfaces import ValidationError
from zope.schema.interfaces import IVocabularyRegistry
from zope.schema.interfaces import IVocabulary, IVocabularyTokenized
from zope.schema.interfaces import ITreeVocabulary
from zope.schema.interfaces import ITokenizedTerm, ITitledTokenizedTerm

# simple vocabularies performing enumerated-like tasks
_marker = object()

@implementer(ITokenizedTerm)
class SimpleTerm(object):
    """Simple tokenized term used by SimpleVocabulary."""

    def __init__(self, value, token=None, title=None):
        """Create a term for value and token. If token is omitted,
        str(value) is used for the token.  If title is provided, 
        term implements ITitledTokenizedTerm.
        """
        self.value = value
        if token is None:
            token = value
        self.token = str(token)
        self.title = title
        if title is not None:
            directlyProvides(self, ITitledTokenizedTerm)

@implementer(IVocabularyTokenized)
class SimpleVocabulary(object):
    """Vocabulary that works from a sequence of terms."""

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
            if term.value in self.by_value:
                raise ValueError(
                    'term values must be unique: %s' % repr(term.value))
            if term.token in self.by_token:
                raise ValueError(
                    'term tokens must be unique: %s' % repr(term.token))
            self.by_value[term.value] = term
            self.by_token[term.token] = term
        if interfaces:
            directlyProvides(self, *interfaces)

    @classmethod
    def fromItems(cls, items, *interfaces):
        """Construct a vocabulary from a list of (token, value) pairs.

        The order of the items is preserved as the order of the terms
        in the vocabulary.  Terms are created by calling the class
        method createTerm() with the pair (value, token).

        One or more interfaces may also be provided so that alternate
        widgets may be bound without subclassing.
        """
        terms = [cls.createTerm(value, token) for (token, value) in items]
        return cls(terms, *interfaces)

    @classmethod
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

    @classmethod
    def createTerm(cls, *args):
        """Create a single term from data.

        Subclasses may override this with a class method that creates
        a term of the appropriate type from the arguments.
        """
        return SimpleTerm(*args)

    def __contains__(self, value):
        """See zope.schema.interfaces.IBaseVocabulary"""
        try:
            return value in self.by_value
        except TypeError:
            # sometimes values are not hashable
            return False

    def getTerm(self, value):
        """See zope.schema.interfaces.IBaseVocabulary"""
        try:
            return self.by_value[value]
        except KeyError:
            raise LookupError(value)

    def getTermByToken(self, token):
        """See zope.schema.interfaces.IVocabularyTokenized"""
        try:
            return self.by_token[token]
        except KeyError:
            raise LookupError(token)

    def __iter__(self):
        """See zope.schema.interfaces.IIterableVocabulary"""
        return iter(self._terms)

    def __len__(self):
        """See zope.schema.interfaces.IIterableVocabulary"""
        return len(self.by_value)


def _createTermTree(tree, branch):
    """ Helper method that creates a tree-like dict with ITokenizedTerm 
    objects as keys from a similar tree with tuples as keys.

    See fromDict for more details.
    """
    for key in branch.keys():
        term = SimpleTerm(key[1], key[0], key[-1])
        tree[term] = {}
        _createTermTree(tree[term], branch[key])
    return tree 


@implementer(ITreeVocabulary)
class TreeVocabulary(object):
    """ Vocabulary that relies on a tree (i.e nested) structure.
    """
    # The default implementation uses a dict to create the tree structure. This
    # can however be overridden in a subclass by any other IEnumerableMapping
    # compliant object type. Python 2.7's OrderableDict for example.
    terms_factory = OrderedDict

    def __init__(self, terms, *interfaces):
        """Initialize the vocabulary given a recursive dict (i.e a tree) with 
        ITokenizedTerm objects for keys and self-similar dicts representing the 
        branches for values.

        Refer to the method fromDict for more details.

        Concerning the ITokenizedTerm keys, the 'value' and 'token' attributes of
        each key (including nested ones) must be unique.

        One or more interfaces may also be provided so that alternate
        widgets may be bound without subclassing.
        """
        self._terms = self.terms_factory()
        self._terms.update(terms)
        self.path_index = self._getPathIndex(terms, {}, 'value')
        self.by_value = self._flattenTree(terms, {}, 'value')
        self.by_token = self._flattenTree(terms, {}, 'token')

        if interfaces:
            directlyProvides(self, *interfaces)
            
    def __contains__(self, value):
        """ See zope.schema.interfaces.IBaseVocabulary

        D.__contains__(k) -> True if D has a key k, else False
        """
        try:
            return value in self.by_value
        except TypeError:
            # sometimes values are not hashable
            return False
    
    def __getitem__(self, key):
        """x.__getitem__(y) <==> x[y]
        """
        return self._terms.__getitem__(key)

    def __iter__(self):
        """See zope.schema.interfaces.IIterableVocabulary
        
        x.__iter__() <==> iter(x)
        """
        return self._terms.__iter__()

    def __len__(self):
        """x.__iter__() <==> iter(x)
        """
        return self._terms.__len__()

    def get(self, key, default=None):
        """Get a value for a key

        The default is returned if there is no value for the key.
        """
        return self._terms.get(key, default)
        
    def keys(self):
        """Return the keys of the mapping object.
        """
        return self._terms.keys()

    def values(self):
        """Return the values of the mapping object.
        """
        return self._terms.values()

    def items(self):
        """Return the items of the mapping object.
        """
        return self._terms.items()

    @classmethod
    def fromDict(cls, dict_, *interfaces):
        """Constructs a vocabulary from a dictionary with tuples as keys.
        The tuples can have 2 or three values, i.e: 
        (token, value, title) or (token, value)
        
        For example, a dict with 2-valued tuples:  

        dict_ = {
            ('exampleregions', 'Regions used in ATVocabExample'): {
                ('aut', 'Austria'): {
                    ('tyr', 'Tyrol'): {
                        ('auss', 'Ausserfern'): {},
                    }
                },
                ('ger', 'Germany'): {
                    ('bav', 'Bavaria'):{}
                },
            }
        }
        One or more interfaces may also be provided so that alternate
        widgets may be bound without subclassing.
        """
        return cls(_createTermTree({}, dict_), *interfaces)

    def _flattenTree(self, tree, dict_, attr):
        """A helper method to create a flat (non-nested) dictionary from a 
        tree. 
        
        Each key of the dictionary is the attribute "attr" of a node in
        the tree, with the value being the corresponding node.

        tree:  The tree (a nested/recursive dictionary) that must be flattened.
        dict_: Dictionary to contain the flattened tree.
        attr:  The attribute of the tree nodes that should be the key in the
               flattened tree.
        """
        for term in tree.keys():
            attrval = getattr(term, attr)
            if attrval in dict_:
                raise ValueError(
                    'term %ss must be unique: %s' \
                        % (attr, repr(attrval)))

            dict_[attrval] = term
            self._flattenTree(tree[term], dict_, attr)
        return dict_
    
    def _getPathIndex(self, tree, index, attr):
        """ Create an index of all the paths of all the nodes, keyed by the
        nodes' values.
        
        This allows for a quick lookup of a node's tree-path, given its value.
        """
        for term in tree.keys():
            attrval = getattr(term, attr)
            if term.value not in index:
               index[attrval] = \
                        self._getPathToTreeNode(self, term.value)
            self._getPathIndex(tree[term], index, attr)
        return index

    def getTerm(self, value):
        """See zope.schema.interfaces.IBaseVocabulary"""
        try:
            return self.by_value[value]
        except KeyError:
            raise LookupError(value)

    def getTermByToken(self, token):
        """See zope.schema.interfaces.IVocabularyTokenized"""
        try:
            return self.by_token[token]
        except KeyError:
            raise LookupError(token)

    def _getPathToTreeNode(self, tree, node):
        """Helper method that computes the path in the tree from the root
        to the given node.

        The tree must be a recursive IEnumerableMapping object.
        """
        path = []
        for parent, child in tree.items():
            if node == parent.value:
                return [node]
            path = self._getPathToTreeNode(child, node)
            if path:
                path.insert(0, parent.value)
                break
        return path 

    def getTermPath(self, value):
        """Returns a list of strings representing the path from the root node 
        to the node with the given value in the tree. 

        Returns an empty string if no node has that value.
        """
        return self.path_index.get(value, [])

# registry code
class VocabularyRegistryError(LookupError):
    def __init__(self, name):
        self.name = name
        Exception.__init__(self, str(self))

    def __str__(self):
        return "unknown vocabulary: %r" % self.name


@implementer(IVocabularyRegistry)
class VocabularyRegistry(object):
    __slots__ = '_map',

    def __init__(self):
        self._map = {}

    def get(self, object, name):
        """See zope.schema.interfaces.IVocabularyRegistry""" 
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
