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
"""Test checkers for standard types

This is a test of the assertions made in
zope.security.checkers._default_checkers.

$Id: test_standard_checkers.py,v 1.3 2003/06/22 20:50:24 jeremy Exp $
"""

from zope.security.checker import ProxyFactory, NamesChecker

def test_dict():
    """Test that we can do everything we expect to be able to do

    with proxied dicts.
    
    >>> d = ProxyFactory({'a': 1, 'b': 2})

    >>> d.clear # Verify that we are protected
    Traceback (most recent call last):
    ...
    ForbiddenAttribute: clear
    >>> d[3] = 4 # Verify that we are protected
    Traceback (most recent call last):
    ...
    ForbiddenAttribute: __setitem__

    >>> d['a']
    1
    >>> len(d)
    2
    >>> list(d)
    ['a', 'b']
    >>> d.get('a')
    1
    >>> int(d.has_key('a'))
    1
    
    >>> c = d.copy()
    >>> c.clear
    Traceback (most recent call last):
    ...
    ForbiddenAttribute: clear
    >>> int(str(c) in ("{'a': 1, 'b': 2}", "{'b': 2, 'a': 1}"))
    1

    >>> int(`c` in ("{'a': 1, 'b': 2}", "{'b': 2, 'a': 1}"))
    1


    >>> def sorted(x):
    ...    x = list(x)
    ...    x.sort()
    ...    return x

    >>> sorted(d.keys())
    ['a', 'b']
    >>> sorted(d.values())
    [1, 2]
    >>> sorted(d.items())
    [('a', 1), ('b', 2)]

    >>> sorted(d.iterkeys())
    ['a', 'b']
    >>> sorted(d.itervalues())
    [1, 2]
    >>> sorted(d.iteritems())
    [('a', 1), ('b', 2)]

    Always available:
    
    >>> int(d < d)
    0
    >>> int(d > d)
    0
    >>> int(d <= d)
    1
    >>> int(d >= d)
    1
    >>> int(d == d)
    1
    >>> int(d != d)
    0
    >>> int(bool(d))
    1
    >>> int(d.__class__ == dict)
    1

    """

def test_list():
    """Test that we can do everything we expect to be able to do

    with proxied lists.
    
    >>> l = ProxyFactory([1, 2])
    >>> del l[0]
    Traceback (most recent call last):
    ...
    ForbiddenAttribute: __delitem__
    >>> l[0] = 3
    Traceback (most recent call last):
    ...
    ForbiddenAttribute: __setitem__
    >>> l[0]
    1
    >>> l[0:1]
    [1]
    >>> l[:1][0]=2
    Traceback (most recent call last):
    ...
    ForbiddenAttribute: __setitem__
    >>> len(l)
    2
    >>> tuple(l)
    (1, 2)
    >>> int(1 in l)
    1
    >>> l.index(2)
    1
    >>> l.count(2)
    1
    >>> str(l)
    '[1, 2]'
    >>> `l`
    '[1, 2]'
    >>> l + l
    [1, 2, 1, 2]

    Always available:
    
    >>> int(l < l)
    0
    >>> int(l > l)
    0
    >>> int(l <= l)
    1
    >>> int(l >= l)
    1
    >>> int(l == l)
    1
    >>> int(l != l)
    0
    >>> int(bool(l))
    1
    >>> int(l.__class__ == list)
    1

        
    """

def test_tuple():
    """Test that we can do everything we expect to be able to do

    with proxied lists.
    
    >>> l = ProxyFactory((1, 2))
    >>> l[0]
    1
    >>> l[0:1]
    (1,)
    >>> len(l)
    2
    >>> list(l)
    [1, 2]
    >>> int(1 in l)
    1
    >>> str(l)
    '(1, 2)'
    >>> `l`
    '(1, 2)'
    >>> l + l
    (1, 2, 1, 2)

    Always available:
    
    >>> int(l < l)
    0
    >>> int(l > l)
    0
    >>> int(l <= l)
    1
    >>> int(l >= l)
    1
    >>> int(l == l)
    1
    >>> int(l != l)
    0
    >>> int(bool(l))
    1
    >>> int(l.__class__ == tuple)
    1
        
    """

def test_iter():
    """
    >>> list(ProxyFactory(iter([1, 2])))
    [1, 2]
    >>> list(ProxyFactory(iter((1, 2))))
    [1, 2]
    >>> list(ProxyFactory(iter({1:1, 2:2})))
    [1, 2]
    >>> def f():
    ...     for i in 1, 2:
    ...             yield i
    ...
    >>> list(ProxyFactory(f()))
    [1, 2]
    >>> list(ProxyFactory(f)())
    [1, 2]
    """

def test_new_class():
    """

    >>> class C(object):
    ...    x = 1
    >>> C = ProxyFactory(C)
    >>> C()
    Traceback (most recent call last):
    ...
    ForbiddenAttribute: __call__
    >>> C.__dict__
    Traceback (most recent call last):
    ...
    ForbiddenAttribute: __dict__
    >>> s = str(C)
    >>> s = `C`
    >>> int(C.__module__ == __name__)
    1
    >>> len(C.__bases__)
    1
    >>> len(C.__mro__)
    2
    
    Always available:
    
    >>> int(C < C)
    0
    >>> int(C > C)
    0
    >>> int(C <= C)
    1
    >>> int(C >= C)
    1
    >>> int(C == C)
    1
    >>> int(C != C)
    0
    >>> int(bool(C))
    1
    >>> int(C.__class__ == type)
    1
    
    """

def test_new_instance():
    """

    >>> class C(object):
    ...    x, y = 1, 2
    >>> c = ProxyFactory(C(), NamesChecker(['x']))
    >>> c.y
    Traceback (most recent call last):
    ...
    ForbiddenAttribute: y
    >>> c.z
    Traceback (most recent call last):
    ...
    ForbiddenAttribute: z
    >>> c.x
    1
    >>> int(c.__class__ == C)
    1
    
    Always available:
    
    >>> int(c < c)
    0
    >>> int(c > c)
    0
    >>> int(c <= c)
    1
    >>> int(c >= c)
    1
    >>> int(c == c)
    1
    >>> int(c != c)
    0
    >>> int(bool(c))
    1
    >>> int(c.__class__ == C)
    1
    
    """

def test_classic_class():
    """

    >>> class C:
    ...    x = 1
    >>> C = ProxyFactory(C)
    >>> C()
    Traceback (most recent call last):
    ...
    ForbiddenAttribute: __call__
    >>> C.__dict__
    Traceback (most recent call last):
    ...
    ForbiddenAttribute: __dict__
    >>> s = str(C)
    >>> s = `C`
    >>> int(C.__module__ == __name__)
    1
    >>> len(C.__bases__)
    0
    
    Always available:
    
    >>> int(C < C)
    0
    >>> int(C > C)
    0
    >>> int(C <= C)
    1
    >>> int(C >= C)
    1
    >>> int(C == C)
    1
    >>> int(C != C)
    0
    >>> int(bool(C))
    1
    
    """

def test_classic_instance():
    """

    >>> class C:
    ...    x, y = 1, 2
    >>> c = ProxyFactory(C(), NamesChecker(['x']))
    >>> c.y
    Traceback (most recent call last):
    ...
    ForbiddenAttribute: y
    >>> c.z
    Traceback (most recent call last):
    ...
    ForbiddenAttribute: z
    >>> c.x
    1
    >>> int(c.__class__ == C)
    1
    
    Always available:
    
    >>> int(c < c)
    0
    >>> int(c > c)
    0
    >>> int(c <= c)
    1
    >>> int(c >= c)
    1
    >>> int(c == c)
    1
    >>> int(c != c)
    0
    >>> int(bool(c))
    1
    >>> int(c.__class__ == C)
    1
    
    """
    
def test_rocks():
    """
    >>> int(type(ProxyFactory(  object()  )) is object)
    1
    >>> int(type(ProxyFactory(  1  )) is int)
    1
    >>> int(type(ProxyFactory(  1.0  )) is float)
    1
    >>> int(type(ProxyFactory(  1l  )) is long)
    1
    >>> int(type(ProxyFactory(  1j  )) is complex)
    1
    >>> int(type(ProxyFactory(  None  )) is type(None))
    1
    >>> int(type(ProxyFactory(  'xxx'  )) is str)
    1
    >>> int(type(ProxyFactory(  u'xxx'  )) is unicode)
    1
    >>> int(type(ProxyFactory(  True  )) is type(True))
    1

    >>> from datetime import timedelta, datetime, date, time
    >>> int(type(ProxyFactory(  timedelta(1)  )) is timedelta)
    1
    >>> int(type(ProxyFactory(  datetime(2000, 1, 1)  )) is datetime)
    1
    >>> int(type(ProxyFactory(  date(2000, 1, 1)  )) is date)
    1
    >>> int(type(ProxyFactory(  time()  )) is time)
    1
    """


    
from zope.testing.doctestunit import DocTestSuite

def test_suite():
    return DocTestSuite()

if __name__ == '__main__':
    import unittest
    unittest.main()
