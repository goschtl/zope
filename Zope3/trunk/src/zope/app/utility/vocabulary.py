##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Utility Vocabulary.

This vocabulary provides terms for all utilities providing a given interface. 

$Id: vocabulary.py,v 1.3 2004/05/07 23:21:13 garrett Exp $
"""
from zope.interface import implements, Interface
from zope.interface.interfaces import IInterface
from zope.interface.verify import verifyObject
from zope.schema.interfaces import IVocabulary, IVocabularyTokenized
from zope.schema.interfaces import IIterableVocabularyQuery
from zope.schema.interfaces import ITokenizedTerm

from zope.app import zapi
from zope.app.interface.vocabulary import ObjectInterfacesVocabulary


class UtilityQuery(object):
    """Query object for utilities.

    >>> vocab = UtilityVocabulary(None, IInterface)
    >>> query = UtilityQuery(vocab)
    >>> verifyObject(IIterableVocabularyQuery, query)
    True

    >>> query.vocabulary is vocab
    True
    """
    implements(IIterableVocabularyQuery)

    vocabulary = None

    def __init__(self, vocabulary):
        self.vocabulary = vocabulary


class UtilityTerm(object):
    """A term representing a utility.

    The token of the term is the name of the utility. Here is a brief example
    on how the IVocabulary interface is handled in this term as a utility:

    >>> term = UtilityTerm(IVocabulary, 'zope.schema.interfaces.IVocabulary')
    >>> verifyObject(ITokenizedTerm, term)
    True

    >>> term.value
    <InterfaceClass zope.schema.interfaces.IVocabulary>
    >>> term.token
    'zope.schema.interfaces.IVocabulary'

    >>> term
    <UtiltiyTerm zope.schema.interfaces.IVocabulary, instance of InterfaceClass>
    """
    implements(ITokenizedTerm)

    def __init__(self, value, token):
        """Create a term for value and token."""
        self.value = value
        self.token = token

    def __repr__(self):
        return '<UtiltiyTerm %s, instance of %s>' %(
            self.token, self.value.__class__.__name__)


class UtilityVocabulary(object):
    """Vocabulary that provides utilities of a specified.

    Here is a short example of how the vocabulary should work.

    First we need to create a utility interface and some utilities:

    >>> class IObject(Interface):
    ...     'Simple interface to mark object utilities.'
    >>>
    >>> class Object(object):
    ...     implements(IObject)
    ...     def __init__(self, name):
    ...         self.name = name
    ...     def __repr__(self):
    ...         return '<Object %s>' %self.name

    Now we register some utilities for IObject

    >>> from zope.app.tests import ztapi
    >>> object1 = Object('object1')
    >>> ztapi.provideUtility(IObject, object1, 'object1')
    >>> object2 = Object('object2')
    >>> ztapi.provideUtility(IObject, object2, 'object2')
    >>> object3 = Object('object3')
    >>> ztapi.provideUtility(IObject, object3, 'object3')
    >>> object4 = Object('object4')

    We are now ready to create a vocabulary that we can use; in our case
    everything is global, so the context is None.

    >>> vocab = UtilityVocabulary(None, IObject)
    >>> import pprint
    >>> pprint.pprint(vocab._terms.items())
    [(u'object1', <UtiltiyTerm object1, instance of Object>),
     (u'object2', <UtiltiyTerm object2, instance of Object>),
     (u'object3', <UtiltiyTerm object3, instance of Object>)]

    Now let's see how the other methods behave in this context. First we can
    just use the 'in' opreator to test whether a value is available.

    >>> object1 in vocab
    True
    >>> object4 in vocab
    False

    We can also create a lazy iterator. Note that the utility terms might
    appear in a different order than the utilities were registered. 

    >>> iterator = iter(vocab)
    >>> terms = list(iterator)
    >>> names = [term.token for term in terms]
    >>> names.sort()
    >>> names
    [u'object1', u'object2', u'object3']

    Determining the amount of utilities available via the vocabulary is also
    possible.

    >>> len(vocab)
    3

    Next we are looking at some of the more vocabulary-characteristic API
    methods. First, there is always a query available for the vocabulary:

    >>> vocab.getQuery().__class__.__name__
    'UtilityQuery'

    One can get a term for a given value using getTerm():

    >>> vocab.getTerm(object1)
    <UtiltiyTerm object1, instance of Object>
    >>> vocab.getTerm(object4)
    Traceback (most recent call last):
    ...
    LookupError: <Object object4>

    On the other hand, if you want to get a term by the token, then you do
    that with:

    >>> vocab.getTermByToken('object1')
    <UtiltiyTerm object1, instance of Object>
    >>> vocab.getTermByToken('object4')
    Traceback (most recent call last):
    ...
    LookupError: object4

    That's it. It is all pretty straight forward, but it allows us to easily
    create a vocabulary for any utility. In fact, to make it easy to register
    such a vocabulary via ZCML, the 'interface' argument to the constructor
    can be a string that is resolved via the utility registry. The ZCML looks
    like this:

    <zope:vocabulary
        name='IObjects'
        interface='zope.app.utility.vocabulary.IObject' />

    >>> ztapi.provideUtility(IInterface, IObject,
    ...                      'zope.app.utility.vocabulary.IObject')
    >>> vocab = UtilityVocabulary(None, 'zope.app.utility.vocabulary.IObject')
    >>> pprint.pprint(vocab._terms.items())
    [(u'object1', <UtiltiyTerm object1, instance of Object>),
     (u'object2', <UtiltiyTerm object2, instance of Object>),
     (u'object3', <UtiltiyTerm object3, instance of Object>)]

    Sometimes it is desirable to only select the name of a utility. For
    this purpose a 'nameOnly' argument was added to the constructor, in which
    case the UtilityTerm's value is not the utility itself but the name of the
    utility.  

    >>> vocab = UtilityVocabulary(None, IObject, nameOnly=True)
    >>> pprint.pprint([term.value for term in vocab])
    [u'object1', u'object2', u'object3']
    """

    implements(IVocabulary, IVocabularyTokenized)

    def __init__(self, context, interface, nameOnly=False):
        if nameOnly is not False:
            nameOnly = True
        if isinstance(interface, (str, unicode)): 
            interface = zapi.getUtility(context, IInterface, interface)
        utils = zapi.getUtilitiesFor(context, interface)
        self._terms = dict([(name, UtilityTerm(nameOnly and name or util, name))
                            for name, util in utils])
      
    def __contains__(self, value):
        """See zope.schema.interfaces.IBaseVocabulary"""
        return value in [term.value for term in self._terms.values()]

    def getQuery(self):
        """See zope.schema.interfaces.IBaseVocabulary"""
        return UtilityQuery(self)

    def getTerm(self, value):
        """See zope.schema.interfaces.IBaseVocabulary"""
        try:
            return [term for name, term in self._terms.items()
                    if term.value == value][0]
        except IndexError:
            raise LookupError, value

    def getTermByToken(self, token):
        """See zope.schema.interfaces.IVocabularyTokenized"""
        try:
            return self._terms[token]
        except KeyError:
            raise LookupError, token

    def __iter__(self):
        """See zope.schema.interfaces.IIterableVocabulary"""
        return iter(self._terms.values())

    def __len__(self):
        """See zope.schema.interfaces.IIterableVocabulary"""
        return len(self._terms)
        

class UtilityComponentInterfacesVocabulary(ObjectInterfacesVocabulary):
    
    def __init__(self, registration):
        super(UtilityComponentInterfacesVocabulary, self).__init__(
            registration.getComponent())