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
"""XXX short summary goes here.

XXX longer description goes here.

$Id: test_context.py,v 1.3 2003/06/02 17:43:02 stevea Exp $
"""

import pickle
import unittest
from zope.app.context import Wrapper
from zope.interface import Interface, implements, directlyProvides, providedBy
from zope.interface import directlyProvidedBy, implementedBy
from zope.testing.doctestunit import DocTestSuite

class I1(Interface):
    pass
class I2(Interface):
    pass
class I3(Interface):
    pass
class I4(Interface):
    pass

class D1(Wrapper):
  implements(I1)

class D2(Wrapper):
  implements(I2)

def test_providedBy_iter_w_new_style_class():
    """
    >>> class X(object):
    ...   implements(I3)

    >>> x = X()
    >>> directlyProvides(x, I4)

    >>> [interface.__name__ for interface in list(providedBy(x))]
    ['I4', 'I3']

    >>> [interface.__name__ for interface in list(providedBy(D1(x)))]
    ['I4', 'I3', 'I1']

    >>> [interface.__name__ for interface in list(providedBy(D2(D1(x))))]
    ['I4', 'I3', 'I1', 'I2']
    """

def test_providedBy_signature_w_new_style_class():
    """
    >>> class X(object):
    ...   implements(I3)

    >>> x = X()

    >>> int(providedBy(x).__signature__ == implementedBy(X).__signature__)
    1

    >>> int(providedBy(Wrapper(x)).__signature__ ==
    ...     implementedBy(X).__signature__)
    1

    >>> directlyProvides(x, I4)    
    >>> int(providedBy(x).__signature__ ==
    ...      (directlyProvidedBy(x).__signature__,
    ...       implementedBy(X).__signature__,
    ...      )
    ...     )
    1

    >>> int(providedBy(D1(x)).__signature__ ==
    ...      (
    ...       (directlyProvidedBy(x).__signature__,
    ...        implementedBy(X).__signature__,
    ...       ),
    ...       implementedBy(D1).__signature__,
    ...      )
    ...     )
    1

    >>> int(providedBy(D2(D1(x))).__signature__ ==
    ...       (
    ...        (
    ...         (directlyProvidedBy(x).__signature__,
    ...          implementedBy(X).__signature__,
    ...         ),
    ...         implementedBy(D1).__signature__,
    ...        ),
    ...        implementedBy(D2).__signature__,
    ...       )
    ...     )
    1

    """

def test_providedBy_signature_w_classic_class():
    """
    >>> class X:
    ...   implements(I3)

    >>> x = X()


    >>> int(providedBy(x).__signature__ == implementedBy(X).__signature__)
    1

    >>> int(providedBy(Wrapper(x)).__signature__ ==
    ...     implementedBy(X).__signature__)
    1

    >>> directlyProvides(x, I4)

    >>> int(providedBy(x).__signature__ ==
    ...      (directlyProvidedBy(x).__signature__,
    ...       implementedBy(X).__signature__,
    ...      )
    ...     )
    1

    >>> int(providedBy(D1(x)).__signature__ ==
    ...      (
    ...       (directlyProvidedBy(x).__signature__,
    ...        implementedBy(X).__signature__,
    ...       ),
    ...       implementedBy(D1).__signature__,
    ...      )
    ...     )
    1

    >>> int(providedBy(D2(D1(x))).__signature__ ==
    ...       (
    ...        (
    ...         (directlyProvidedBy(x).__signature__,
    ...          implementedBy(X).__signature__,
    ...         ),
    ...         implementedBy(D1).__signature__,
    ...        ),
    ...        implementedBy(D2).__signature__,
    ...       )
    ...     )
    1

    """

def test_ContextWrapper_basic():
    """
    >>> from zope.security.checker import ProxyFactory, NamesChecker
    >>> checker = NamesChecker()
    >>> from zope.context import ContainmentIterator
    >>> from zope.app.context import ContextWrapper
    >>> from zope.context import getWrapperData

    >>> class C:
    ...    def __init__(self, name): self.name = name
    ...    def __repr__(self): return self.name

    >>> c1 = C('c1')

    >>> c2 = C('c2')
    >>> p2 = ProxyFactory(c2)
    >>> w2 = ContextWrapper(p2, c1, name=2)
    >>> int(type(w2) is type(p2))
    1
    >>> getWrapperData(w2)
    {'name': 2}

    >>> c3 = C('c3')
    >>> p3 = ProxyFactory(c3)
    >>> w3 = ContextWrapper(p3, w2, name=3)
    >>> int(type(w3) is type(p3))
    1
    >>> getWrapperData(w3)
    {'name': 3}

    >>> list(ContainmentIterator(w3))
    [c3, c2, c1]

    >>> w3x = ContextWrapper(w3, w2, name='x')
    >>> int(w3x is w3)
    1
    >>> getWrapperData(w3)
    {'name': 'x'}

    """

class Thing:
    pass

def test_pickle_prevention():
    """
    >>> w = Wrapper(Thing(), 2)
    >>> pickle.dumps(w)
    Traceback (most recent call last):
    ...
    PicklingError: Zope context wrappers cannot be pickled
    """

def test_reduce_in_subclass():
    """
    >>> class CustomPicklingError(pickle.PicklingError):
    ...     pass

    >>> class WrapperWithReduce(Wrapper):
    ...     def __reduce__(self):
    ...         raise CustomPicklingError
    ...     def __reduce_ex__(self, proto):
    ...         raise CustomPicklingError

    >>> w = WrapperWithReduce(Thing())
    >>> pickle.dumps(w)
    Traceback (most recent call last):
    ...
    CustomPicklingError
    """

def test_SecurityCheckerDescriptor():
    """Descriptor for a Wrapper that provides a decorated security checker.

    >>> from zope.security.checker import defineChecker, NamesChecker, NoProxy
    >>> from zope.context import Wrapper
    >>> from zope.app.context import DecoratedSecurityCheckerDescriptor
    >>> class MyWrapper(Wrapper):
    ...     __Security_checker__ = DecoratedSecurityCheckerDescriptor()

    >>> class Foo:
    ...     a = 1
    ...     b = 2
    ...     c = 3

    >>> defineChecker(Foo, NamesChecker(['a']))
    >>> defineChecker(MyWrapper, NoProxy)

    >>> w = MyWrapper(Foo())
    >>> from zope.security.checker import selectChecker
    >>> print selectChecker(w)
    None
    >>> c = w.__Security_checker__
    >>> print type(c)
    <class 'zope.security.checker.Checker'>
    >>> c.check_getattr(w, 'a')

    >>> c.check_getattr(w, 'b')
    Traceback (most recent call last):
    ...
    ForbiddenAttribute: b
    >>> c.check_getattr(w, 'c')
    Traceback (most recent call last):
    ...
    ForbiddenAttribute: c

    >>> class MyWrapper2(Wrapper):
    ...     __Security_checker__ = DecoratedSecurityCheckerDescriptor()
    >>> defineChecker(MyWrapper2, NamesChecker(['b']))
    >>> w = MyWrapper2(Foo())
    >>> c = w.__Security_checker__
    >>> print type(c)
    <class 'zope.security.checker.CombinedChecker'>
    >>> c.check_getattr(w, 'a')

    >>> c.check_getattr(w, 'b')

    >>> c.check_getattr(w, 'c')
    Traceback (most recent call last):
    ...
    ForbiddenAttribute: c

    >>> w = MyWrapper(None)
    >>> int(w.__Security_checker__ is None)
    1
    >>> w = MyWrapper2(None)
    >>> type(w.__Security_checker__)
    <class 'zope.security.checker.Checker'>
    """

def test_suite():
    suite = DocTestSuite()
    suite.addTest(DocTestSuite('zope.app.context'))
    return suite


if __name__ == '__main__':
    unittest.main()
