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

$Id: test_modulezcml.py,v 1.1 2003/09/02 20:47:05 jim Exp $
"""
import unittest
from zope.testing.doctestunit import DocTestSuite
from zope.app.security.registries.permissionregistry import permissionRegistry
import zope.interface
from zope.app.security import modulezcml
from zope.security.checker import moduleChecker
from pprint import PrettyPrinter

def pprint(ob, width=70):
    PrettyPrinter(width=width).pprint(ob)

class I1(zope.interface.Interface):
    def x(): pass
    y = zope.interface.Attribute("Y")

class I2(I1):
    def a(): pass
    b = zope.interface.Attribute("B")

test_perm = 'zope.app.security.modulezcml.test'
test_bad_perm = 'zope.app.security.modulezcml.bad'

def test_protectModule():
    """
    >>> from zope.app.security.tests import test_modulezcml

    Initially, there's no checker defined for the module:

    >>> moduleChecker(test_modulezcml)
    
    Should get an ewrror if a permission is defined before it's used:

    >>> modulezcml.protectModule(test_modulezcml, 'foo', test_perm)
    Traceback (most recent call last):
    ...
    UndefinedPermissionError: zope.app.security.modulezcml.test
    
    >>> perm = permissionRegistry.definePermission(test_perm, '')
    >>> modulezcml.protectModule(test_modulezcml, 'foo', test_perm)

    Now, the checker should exist and have an access dictionary with the
    name and permission:

    >>> checker = moduleChecker(test_modulezcml)
    >>> cdict = checker.getPermission_func().__self__
    >>> pprint(cdict)
    {'foo': 'zope.app.security.modulezcml.test'}
    
    If we define additional names, they will be added to the dict:

    >>> modulezcml.protectModule(test_modulezcml, 'bar', test_perm)
    >>> modulezcml.protectModule(test_modulezcml, 'baz', test_perm)
    >>> pprint(cdict)
    {'bar': 'zope.app.security.modulezcml.test',
     'baz': 'zope.app.security.modulezcml.test',
     'foo': 'zope.app.security.modulezcml.test'}
        
    """

def test_allow():
    """

    The allow directive creates actions for each named defined
    directly, or via interface:

    >>> class Context:
    ...     def __init__(self):
    ...         self.actions = []
    ...     def action(self, discriminator, callable, args):
    ...         self.actions.append(
    ...             {'discriminator': discriminator,
    ...              'callable': int(callable is modulezcml.protectModule),
    ...              'args': args})
    ...     module='testmodule'

    >>> context = Context()
    >>> modulezcml.allow(context, attributes=['foo', 'bar'],
    ...                           interface=[I1, I2])

    >>> context.actions.sort(
    ...    lambda a, b: cmp(a['discriminator'], b['discriminator']))
    >>> pprint(context.actions)
    [{'args': ('testmodule', 'a', 'zope.Public'),
      'callable': 1,
      'discriminator': ('http://namespaces.zope.org/zope:module',
                        'testmodule',
                        'a')},
     {'args': ('testmodule', 'b', 'zope.Public'),
      'callable': 1,
      'discriminator': ('http://namespaces.zope.org/zope:module',
                        'testmodule',
                        'b')},
     {'args': ('testmodule', 'bar', 'zope.Public'),
      'callable': 1,
      'discriminator': ('http://namespaces.zope.org/zope:module',
                        'testmodule',
                        'bar')},
     {'args': ('testmodule', 'foo', 'zope.Public'),
      'callable': 1,
      'discriminator': ('http://namespaces.zope.org/zope:module',
                        'testmodule',
                        'foo')},
     {'args': ('testmodule', 'x', 'zope.Public'),
      'callable': 1,
      'discriminator': ('http://namespaces.zope.org/zope:module',
                        'testmodule',
                        'x')},
     {'args': ('testmodule', 'y', 'zope.Public'),
      'callable': 1,
      'discriminator': ('http://namespaces.zope.org/zope:module',
                        'testmodule',
                        'y')}]

    """

def test_require():
    """

    The allow directive creates actions for each named defined
    directly, or via interface:

    >>> class Context:
    ...     def __init__(self):
    ...         self.actions = []
    ...     def action(self, discriminator, callable, args):
    ...         self.actions.append(
    ...             {'discriminator': discriminator,
    ...              'callable': int(callable is modulezcml.protectModule),
    ...              'args': args})
    ...     module='testmodule'

    >>> context = Context()
    >>> modulezcml.require(context, attributes=['foo', 'bar'],
    ...                    interface=[I1, I2], permission='p')

    >>> context.actions.sort(
    ...    lambda a, b: cmp(a['discriminator'], b['discriminator']))
    >>> pprint(context.actions)
    [{'args': ('testmodule', 'a', 'p'),
      'callable': 1,
      'discriminator': ('http://namespaces.zope.org/zope:module',
                        'testmodule',
                        'a')},
     {'args': ('testmodule', 'b', 'p'),
      'callable': 1,
      'discriminator': ('http://namespaces.zope.org/zope:module',
                        'testmodule',
                        'b')},
     {'args': ('testmodule', 'bar', 'p'),
      'callable': 1,
      'discriminator': ('http://namespaces.zope.org/zope:module',
                        'testmodule',
                        'bar')},
     {'args': ('testmodule', 'foo', 'p'),
      'callable': 1,
      'discriminator': ('http://namespaces.zope.org/zope:module',
                        'testmodule',
                        'foo')},
     {'args': ('testmodule', 'x', 'p'),
      'callable': 1,
      'discriminator': ('http://namespaces.zope.org/zope:module',
                        'testmodule',
                        'x')},
     {'args': ('testmodule', 'y', 'p'),
      'callable': 1,
      'discriminator': ('http://namespaces.zope.org/zope:module',
                        'testmodule',
                        'y')}]
    
    """


def test_suite():
    return unittest.TestSuite((
        DocTestSuite(),
        ))

if __name__ == '__main__': unittest.main()
