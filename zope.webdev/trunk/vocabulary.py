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
"""Utility Vocabulary.

This vocabulary provides terms for all utilities providing a given interface.

$Id$
"""
__docformat__ = "reStructuredText"


from zope.interface import implements
from zope.interface.interfaces import IInterface
from zope.schema.interfaces import ITokenizedTerm
from zope.component.interfaces import IFactory

from zope.app import zapi
from zope.app.component.vocabulary import UtilityVocabulary
from zope.security.management import getInteraction
from zope.app import zapi
from zope.app.schema.vocabulary import IVocabularyFactory 
from zope.schema.vocabulary import SimpleVocabulary,SimpleTerm

# TODO: this vocabulary should go to zope.app.component where the IFactory 
# is located.
class FactoryTerm(object):
    """A term representing a factory.

    The token of the term is the name of the factory. Here is a brief example
    on how the IVocabulary interface is handled in this term as a factory:

    >>> from zope.schema.interfaces import IVocabulary
    >>> from zope.interface.verify import verifyObject
    >>> term = FactoryTerm(IVocabulary, 'zope.schema.interfaces.IVocabulary')
    >>> verifyObject(ITokenizedTerm, term)
    True

    >>> term.value
    <InterfaceClass zope.schema.interfaces.IVocabulary>
    >>> term.token
    'zope.schema.interfaces.IVocabulary'

    >>> term
    <FactoryTerm zope.schema.interfaces.IVocabulary, instance of <InterfaceClass zope.schema.interfaces.IVocabulary>>
    """
    implements(ITokenizedTerm)

    def __init__(self, value, token):
        """Create a term for value and token."""
        self.value = value
        self.token = token

    def __repr__(self):
        return '<FactoryTerm %s, instance of %s>' %(
            self.token, self.value)



# TODO: Cut the too long test output
class FactoryVocabulary(UtilityVocabulary):
    """Vocabulary that provides utilities of a specified interface.

    Here is a short example of how the vocabulary should work.

    First we need to create a utility interface and some utilities:

    >>> from zope.interface import Interface
    >>> from zope.component.factory import Factory
    >>> class IObject(Interface):
    ...     'Simple interface to mark object utilities.'
    >>>
    >>> class Object(object):
    ...     implements(IObject)
    ...     def __init__(self, name):
    ...         self.name = name
    ...     def __repr__(self):
    ...         return '<Object %s>' %self.name

    Now we register a factory for IObject

    >>> from zope.app.testing import ztapi
    >>> factory = Factory(Object, interfaces=(IObject,))
    >>> ztapi.provideUtility(IFactory, factory, 'zope.webdev.vocabulary.IObject')

    We are now ready to create a vocabulary that we can use; in our case
    everything is global, so the context is None.

    >>> vocab = FactoryVocabulary(None, IObject)
    >>> import pprint
    >>> pprint.pprint(vocab._terms.items())
    [(u'zope.webdev.vocabulary.IObject',
      <FactoryTerm zope.webdev.vocabulary.IObject, instance of <Factory for <class 'zope.webdev.vocabulary.Object'>>>)]

    Now let's see how the other methods behave in this context. First we can
    just use the 'in' opreator to test whether a value is available.

    >>> factory in vocab
    True

    We can also create a lazy iterator.

    >>> iterator = iter(vocab)
    >>> terms = list(iterator)
    >>> names = [term.token for term in terms]
    >>> names.sort()
    >>> names
    [u'zope.webdev.vocabulary.IObject']

    Determining the amount of factories available via the vocabulary is also
    possible.

    >>> len(vocab)
    1

    Next we are looking at some of the more vocabulary-characteristic API
    methods.

    One can get a term for a given value using ``getTerm()``:

    >>> vocab.getTerm(factory)
    <FactoryTerm zope.webdev.vocabulary.IObject, instance of <Factory for <class 'zope.webdev.vocabulary.Object'>>>

    On the other hand, if you want to get a term by the token, then you do
    that with:

    >>> vocab.getTermByToken('zope.webdev.vocabulary.IObject')
    <FactoryTerm zope.webdev.vocabulary.IObject, instance of <Factory for <class 'zope.webdev.vocabulary.Object'>>>
    >>> vocab.getTermByToken('noneExist')
    Traceback (most recent call last):
    ...
    LookupError: noneExist

    That's it. It is all pretty straight forward, but it allows us to easily
    create a vocabulary for any factory. In fact, to make it easy to register
    such a vocabulary via ZCML, the `interface` argument to the constructor
    can be a string that is resolved via the utility registry. The ZCML looks
    like this:

    <zope:vocabulary
        name='IObjects'
        factory='zope.webdev.vocabulary.FactoryVocabulary'
        interface='zope.webdev.vocabulary.IObject' />
    >>> ztapi.provideUtility(IInterface, IObject,
    ...                      'zope.webdev.vocabulary.IObject')
    >>> vocab = FactoryVocabulary(None, 'zope.webdev.vocabulary.IObject')
    >>> pprint.pprint(vocab._terms.items())
    [(u'zope.webdev.vocabulary.IObject',
      <FactoryTerm zope.webdev.vocabulary.IObject, instance of <Factory for <class 'zope.webdev.vocabulary.Object'>>>)]

    Sometimes it is desirable to only select the name of a utility. For
    this purpose a `nameOnly` argument was added to the constructor, in which
    case the UtilityTerm's value is not the utility itself but the name of the
    utility.

    >>> vocab = FactoryVocabulary(None, IObject, nameOnly=True)
    >>> pprint.pprint([term.value for term in vocab])
    [u'zope.webdev.vocabulary.IObject']
    """

    def __init__(self, context, interface, nameOnly=False):
        if nameOnly is not False:
            nameOnly = True
        if isinstance(interface, (str, unicode)):
            interface = zapi.getUtility(IInterface, interface)
        self.interface = interface
        utils = zapi.getUtilitiesFor(IFactory)
        factories = []
        for name, factory in utils:
            if interface in factory.getInterfaces():
                if name.startswith('BrowserAdd__'):
                    continue
                factories.append((name, factory))
        self._terms = dict([(name, FactoryTerm(nameOnly and name or util, name))
                            for name, util in factories])
