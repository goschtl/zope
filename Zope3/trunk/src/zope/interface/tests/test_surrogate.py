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

$Id: test_surrogate.py,v 1.2 2003/11/21 17:11:44 jim Exp $
"""
import unittest
from zope.testing.doctestunit import DocTestSuite
from zope.interface.surrogate import SurrogateRegistry
import zope.interface

class IF0(zope.interface.Interface):
    pass
class IF1(IF0):
    pass

class F1:
    zope.interface.implements(IF1)

class IB0(zope.interface.Interface):
    pass
class IB1(IB0):
    pass

class IR0(zope.interface.Interface):
    pass
class IR1(IR0):
    pass

class R1:
    zope.interface.implements(IR1)

class Adapter:
    def __init__(self, *args):
        self.args = args

class A1(Adapter):
    pass

class A2(Adapter):
    pass

def test_multi_adapter_w_default():
    """
    >>> c = F1()
    >>> r = R1()

    >>> registry = SurrogateRegistry()
    
    >>> registry.provideAdapter(None, IB1, [A1], name='bob', with=[IR0])

    >>> a = registry.queryMultiAdapter((c, r), IB0, 'bob')
    >>> a.__class__ is A1
    True
    >>> a.args == (c, r)
    True
    
    >>> registry.queryMultiAdapter((c, r), IB0, 'bruce')

    >>> registry.provideAdapter(None, IB1, [A2], name='bob', with=[IR1])
    >>> a = registry.queryMultiAdapter((c, r), IB0, 'bob')
    >>> a.__class__ is A2
    True
    >>> a.args == (c, r)
    True
    
    """

def test_multi_adapter_w_inherited_and_multiple_registrations():
    """
    >>> c = F1()
    >>> r = R1()

    >>> registry = SurrogateRegistry()

    >>> class IX(zope.interface.Interface):
    ...    pass

    >>> class AX(Adapter):
    ...     pass
    
    >>> registry.provideAdapter(IF0, IB1, [A1], name='bob', with=[IR0])
    >>> registry.provideAdapter(IF1, IB1, [AX], name='bob', with=[IX])

    >>> a = registry.queryMultiAdapter((c, r), IB0, 'bob')
    >>> a.__class__ is A1
    True
    >>> a.args == (c, r)
    True
    """

def test_named_adapter_with_default():
    """Query a named simple adapter

    >>> import zope.interface

    >>> c = F1()

    >>> registry = SurrogateRegistry()

    If we ask for a named adapter, we won't get a result unless there
    is a named adapter, even if the object implements the interface:

    >>> registry.queryNamedAdapter(c, IF0, 'bob')

    >>> registry.provideAdapter(None, IB1, [A1], name='bob')
    >>> a = registry.queryNamedAdapter(c, IB0, 'bob')
    >>> a.__class__ is A1
    True
    >>> a.args == (c, )
    True

    >>> registry.queryNamedAdapter(c, IB0, 'bruce')

    >>> registry.provideAdapter(None, IB0, [A2], name='bob')
    >>> a = registry.queryNamedAdapter(c, IB0, 'bob')
    >>> a.__class__ is A2
    True
    >>> a.args == (c, )
    True


    """

def test_multi_adapter_gets_closest_provided():
    """
    >>> c = F1()
    >>> r = R1()

    >>> registry = SurrogateRegistry()
    >>> registry.provideAdapter(IF1, IB0, [A1], name='bob', with=[IR0])
    >>> registry.provideAdapter(IF1, IB1, [A2], name='bob', with=[IR0])
    >>> a = registry.queryMultiAdapter((c, r), IB0, 'bob')
    >>> a.__class__ is A1
    True

    >>> registry = SurrogateRegistry()
    >>> registry.provideAdapter(IF1, IB1, [A2], name='bob', with=[IR0])
    >>> registry.provideAdapter(IF1, IB0, [A1], name='bob', with=[IR0])
    >>> a = registry.queryMultiAdapter((c, r), IB0, 'bob')
    >>> a.__class__ is A1
    True

    >>> registry = SurrogateRegistry()
    >>> registry.provideAdapter(IF1, IB0, [A1], name='bob', with=[IR0])
    >>> registry.provideAdapter(IF1, IB1, [A2], name='bob', with=[IR1])
    >>> a = registry.queryMultiAdapter((c, r), IB0, 'bob')
    >>> a.__class__ is A2
    True

    >>> registry = SurrogateRegistry()
    >>> registry.provideAdapter(IF1, IB1, [A2], name='bob', with=[IR1])
    >>> registry.provideAdapter(IF1, IB0, [A1], name='bob', with=[IR0])
    >>> a = registry.queryMultiAdapter((c, r), IB0, 'bob')
    >>> a.__class__ is A2
    True

    """

def test_multi_adapter_check_non_default_dont_hide_default():
    """
    >>> c = F1()
    >>> r = R1()

    >>> registry = SurrogateRegistry()

    >>> class IX(zope.interface.Interface):
    ...     pass

    
    >>> registry.provideAdapter(None, IB0, [A1], name='bob', with=[IR0])
    >>> registry.provideAdapter(IF1,  IB0, [A2], name='bob', with=[IX])
    >>> a = registry.queryMultiAdapter((c, r), IB0, 'bob')
    >>> a.__class__.__name__
    'A1'

    """


def test_getRegisteredMatching_with_with():
    """
    >>> registry = SurrogateRegistry()
    >>> registry.provideAdapter(None, IB0, '_0')
    >>> registry.provideAdapter(IF0, IB0, '00')
    >>> registry.provideAdapter(IF1, IB0, '10')
    >>> registry.provideAdapter(IF1, IB1, '11')
    >>> registry.provideAdapter(IF0, IB0, '000', with=(IR0,))
    >>> registry.provideAdapter(IF1, IB0, '100', with=(IR0,))
    >>> registry.provideAdapter(IF1, IB1, '110', with=(IR0,))
    >>> registry.provideAdapter(IF0, IB0, '001', with=(IR1,))
    >>> registry.provideAdapter(IF1, IB0, '101', with=(IR1,))
    >>> registry.provideAdapter(IF1, IB1, '111', with=(IR1,))

    >>> from pprint import PrettyPrinter
    >>> pprint = PrettyPrinter(width=60).pprint
    >>> def sorted(x):
    ...    x = [(getattr(r, '__name__', None), p.__name__,
    ...          [w.__name__ for w in rwith], n, f)
    ...         for (r, p, rwith, n, f) in x]
    ...    x.sort()
    ...    pprint(x)

    >>> sorted(registry.getRegisteredMatching())
    [(None, 'IB0', [], u'', '_0'),
     ('IF0', 'IB0', [], u'', '00'),
     ('IF0', 'IB0', ['IR0'], u'', '000'),
     ('IF0', 'IB0', ['IR1'], u'', '001'),
     ('IF1', 'IB0', [], u'', '10'),
     ('IF1', 'IB0', ['IR0'], u'', '100'),
     ('IF1', 'IB0', ['IR1'], u'', '101'),
     ('IF1', 'IB1', [], u'', '11'),
     ('IF1', 'IB1', ['IR0'], u'', '110'),
     ('IF1', 'IB1', ['IR1'], u'', '111')]
    >>> sorted(registry.getRegisteredMatching(required=[IF0]))
    [(None, 'IB0', [], u'', '_0'),
     ('IF0', 'IB0', [], u'', '00'),
     ('IF0', 'IB0', ['IR0'], u'', '000'),
     ('IF0', 'IB0', ['IR1'], u'', '001')]
    >>> sorted(registry.getRegisteredMatching(required=[IF1],
    ...                                       provided=[IB0]))
    [(None, 'IB0', [], u'', '_0'),
     ('IF0', 'IB0', [], u'', '00'),
     ('IF0', 'IB0', ['IR0'], u'', '000'),
     ('IF0', 'IB0', ['IR1'], u'', '001'),
     ('IF1', 'IB0', [], u'', '10'),
     ('IF1', 'IB0', ['IR0'], u'', '100'),
     ('IF1', 'IB0', ['IR1'], u'', '101'),
     ('IF1', 'IB1', [], u'', '11'),
     ('IF1', 'IB1', ['IR0'], u'', '110'),
     ('IF1', 'IB1', ['IR1'], u'', '111')]
    >>> sorted(registry.getRegisteredMatching(required=[IF1],
    ...                                       provided=[IB0],
    ...                                       with=[IR0]))
    [('IF0', 'IB0', ['IR0'], u'', '000'),
     ('IF1', 'IB0', ['IR0'], u'', '100'),
     ('IF1', 'IB1', ['IR0'], u'', '110')]
    >>> sorted(registry.getRegisteredMatching(required=[IF1],
    ...                                       provided=[IB0],
    ...                                       with=[IR1]))
    [('IF0', 'IB0', ['IR0'], u'', '000'),
     ('IF0', 'IB0', ['IR1'], u'', '001'),
     ('IF1', 'IB0', ['IR0'], u'', '100'),
     ('IF1', 'IB0', ['IR1'], u'', '101'),
     ('IF1', 'IB1', ['IR0'], u'', '110'),
     ('IF1', 'IB1', ['IR1'], u'', '111')]
    """




def test_suite():
    return unittest.TestSuite((
        DocTestSuite('zope.interface.surrogate'),
        DocTestSuite(),
        ))

if __name__ == '__main__': unittest.main()
