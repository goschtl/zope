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
"""Context Tests

$Id: test_decorator.py,v 1.2 2003/09/21 17:33:33 jim Exp $
"""

import pickle
import unittest
from zope.app.decorator import Decorator
from zope.interface import Interface, implements, directlyProvides, providedBy
from zope.interface import directlyProvidedBy, implementedBy
from zope.testing.doctestunit import DocTestSuite
from zope.exceptions import ForbiddenAttribute

class I1(Interface):
    pass
class I2(Interface):
    pass
class I3(Interface):
    pass
class I4(Interface):
    pass

class D1(Decorator):
  implements(I1)

class D2(Decorator):
  implements(I2)


def check_forbidden_call(callable, *args):
    try:
        return callable(*args)
    except ForbiddenAttribute, e:
        return 'ForbiddenAttribute: %s' % e[0]


def test_providedBy_iter_w_new_style_class():
    """
    >>> class X(object):
    ...   implements(I3)

    >>> x = X()
    >>> directlyProvides(x, I4)

    >>> [interface.getName() for interface in list(providedBy(x))]
    ['I4', 'I3']

    >>> [interface.getName() for interface in list(providedBy(D1(x)))]
    ['I4', 'I3', 'I1']

    >>> [interface.getName() for interface in list(providedBy(D2(D1(x))))]
    ['I4', 'I3', 'I1', 'I2']
    """

def test_providedBy_signature_w_new_style_class():
    """
    >>> class X(object):
    ...   implements(I3)

    >>> x = X()

    >>> int(providedBy(x).__signature__ == implementedBy(X).__signature__)
    1

    >>> int(providedBy(Decorator(x)).__signature__ ==
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

    >>> int(providedBy(Decorator(x)).__signature__ ==
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

class Thing:
    pass

def test_SecurityCheckerDescriptor():
    """Descriptor for a Decorator that provides a decorated security checker.

    >>> from zope.security.checker import defineChecker, NamesChecker, NoProxy
    >>> from zope.app.decorator import DecoratedSecurityCheckerDescriptor
    >>> class MyDecorator(Decorator):
    ...     __Security_checker__ = DecoratedSecurityCheckerDescriptor()

    >>> class Foo:
    ...     a = 1
    ...     b = 2
    ...     c = 3

    >>> defineChecker(Foo, NamesChecker(['a']))
    >>> defineChecker(MyDecorator, NoProxy)

    >>> w = MyDecorator(Foo())
    >>> from zope.security.checker import selectChecker
    >>> print selectChecker(w)
    None
    >>> c = w.__Security_checker__
    >>> print type(c)
    <class 'zope.security.checker.Checker'>
    >>> c.check_getattr(w, 'a')

    >>> check_forbidden_call(c.check_getattr, w, 'b')
    'ForbiddenAttribute: b'
    >>> check_forbidden_call(c.check_getattr, w, 'c')
    'ForbiddenAttribute: c'

    >>> class MyDecorator2(Decorator):
    ...     __Security_checker__ = DecoratedSecurityCheckerDescriptor()
    >>> defineChecker(MyDecorator2, NamesChecker(['b']))
    >>> w = MyDecorator2(Foo())
    >>> c = w.__Security_checker__
    >>> print type(c)
    <class 'zope.security.checker.CombinedChecker'>
    >>> c.check_getattr(w, 'a')

    >>> c.check_getattr(w, 'b')

    >>> check_forbidden_call(c.check_getattr, w, 'c')
    'ForbiddenAttribute: c'

    >>> w = MyDecorator(None)
    >>> int(w.__Security_checker__ is None)
    1
    >>> w = MyDecorator2(None)
    >>> type(w.__Security_checker__)
    <class 'zope.security.checker.Checker'>
    """


def test_suite():
    suite = DocTestSuite()
    suite.addTest(DocTestSuite('zope.app.decorator'))
    return suite


if __name__ == '__main__':
    unittest.main()
