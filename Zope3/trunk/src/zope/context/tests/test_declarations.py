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
"""Test interface declarations on decorator classes.

$Id: test_declarations.py,v 1.1 2003/05/31 22:12:38 jim Exp $
"""

from zope.testing.doctestunit import DocTestSuite

from zope.context import Wrapper
from zope.interface import *

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


def test_iter_w_new_style_class():
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

def test_signature_w_new_style_class():
    """
    >>> class X(object):
    ...   implements(I3)
    
    >>> x = X()
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

def test_signature_w_classic_class():
    """
    >>> class X:
    ...   implements(I3)
    
    >>> x = X()
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

def test_suite():
    suite = DocTestSuite('zope.context.declarations')
    suite.addTest(DocTestSuite())
    return suite

    
if __name__ == '__main__': unittest.main()
