##############################################################################
#
# Copyright (c) 2001 - 2012 Zope Foundation and Contributors.
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
"""Persistent component registry tests
"""
import unittest

from zope.interface import Interface
from zope.interface import implements
from zope.component import adapter
from zope.component.testing import setUp
from zope.component.testing import tearDown


class I1(Interface):
    pass

class I2(Interface):
    pass

class U(object):

    def __init__(self, name):
        self.__name__ = name

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.__name__)

class U1(U):
    implements(I1)

class U12(U):
    implements(I1, I2)

@adapter(I1)
def handle1(x):
    print 'handle1', x

def handle(*objects):
    print 'handle', objects

@adapter(I1)
def handle3(x):
    print 'handle3', x

@adapter(I1)
def handle4(x):
    print 'handle4', x

def test_persistent_component_managers():
    """
Here, we'll demonstrate that changes work even when data are stored in
a database and when accessed from multiple connections.

Start by setting up a database and creating two transaction
managers and database connections to work with.

    >>> from zope.component.testing import setUp, tearDown
    >>> setUp()
    >>> import ZODB.tests.util
    >>> db = ZODB.tests.util.DB()
    >>> import transaction
    >>> t1 = transaction.TransactionManager()
    >>> c1 = db.open(transaction_manager=t1)
    >>> r1 = c1.root()
    >>> t2 = transaction.TransactionManager()
    >>> c2 = db.open(transaction_manager=t2)
    >>> r2 = c2.root()

Create a set of components registries in the database, alternating
connections.

    >>> from zope.component.persistentregistry import PersistentComponents

    >>> _ = t1.begin()
    >>> r1[1] = PersistentComponents('1')
    >>> t1.commit()

    >>> _ = t2.begin()
    >>> r2[2] = PersistentComponents('2', (r2[1], ))
    >>> t2.commit()

    >>> _ = t1.begin()
    >>> r1[3] = PersistentComponents('3', (r1[1], ))
    >>> t1.commit()

    >>> _ = t2.begin()
    >>> r2[4] = PersistentComponents('4', (r2[2], r2[3]))
    >>> t2.commit()

    >>> _ = t1.begin()
    >>> r1[1].__bases__
    ()
    >>> r1[2].__bases__ == (r1[1], )
    True

    >>> r1[1].registerUtility(U1(1))
    >>> r1[1].queryUtility(I1)
    U1(1)
    >>> r1[2].queryUtility(I1)
    U1(1)
    >>> t1.commit()

    >>> _ = t2.begin()
    >>> r2[1].registerUtility(U1(2))
    >>> r2[2].queryUtility(I1)
    U1(2)

    >>> r2[4].queryUtility(I1)
    U1(2)
    >>> t2.commit()


    >>> _ = t1.begin()
    >>> r1[1].registerUtility(U12(1), I2)
    >>> r1[4].queryUtility(I2)
    U12(1)
    >>> t1.commit()


    >>> _ = t2.begin()
    >>> r2[3].registerUtility(U12(3), I2)
    >>> r2[4].queryUtility(I2)
    U12(3)
    >>> t2.commit()

    >>> _ = t1.begin()

    >>> r1[1].registerHandler(handle1, info="First handler")
    >>> r1[2].registerHandler(handle, required=[U])

    >>> r1[3].registerHandler(handle3)

    >>> r1[4].registerHandler(handle4)

    >>> r1[4].handle(U1(1))
    handle1 U1(1)
    handle3 U1(1)
    handle (U1(1),)
    handle4 U1(1)

    >>> t1.commit()

    >>> _ = t2.begin()
    >>> r2[4].handle(U1(1))
    handle1 U1(1)
    handle3 U1(1)
    handle (U1(1),)
    handle4 U1(1)
    >>> t2.abort()

    >>> db.close()
    >>> tearDown()
    """

def persistent_registry_doesnt_scew_up_subsribers():
    """
    >>> from zope.component.testing import setUp, tearDown
    >>> setUp()
    >>> import ZODB.tests.util
    >>> db = ZODB.tests.util.DB()
    >>> import transaction
    >>> t1 = transaction.TransactionManager()
    >>> c1 = db.open(transaction_manager=t1)
    >>> r1 = c1.root()
    >>> t2 = transaction.TransactionManager()
    >>> c2 = db.open(transaction_manager=t2)
    >>> r2 = c2.root()

    >>> from zope.component.persistentregistry import PersistentComponents

    >>> _ = t1.begin()
    >>> r1[1] = PersistentComponents('1')
    >>> r1[1].registerHandler(handle1)
    >>> r1[1].registerSubscriptionAdapter(handle1, provided=I2)
    >>> _ = r1[1].unregisterHandler(handle1)
    >>> _ = r1[1].unregisterSubscriptionAdapter(handle1, provided=I2)
    >>> t1.commit()
    >>> _ = t1.begin()
    >>> r1[1].registerHandler(handle1)
    >>> r1[1].registerSubscriptionAdapter(handle1, provided=I2)
    >>> t1.commit()

    >>> _ = t2.begin()
    >>> len(list(r2[1].registeredHandlers()))
    1
    >>> len(list(r2[1].registeredSubscriptionAdapters()))
    1
    >>> t2.abort()
    >>> tearDown()
    """



class GlobalRegistry:
    pass

from zope.component.globalregistry import GlobalAdapterRegistry
base = GlobalAdapterRegistry(GlobalRegistry, 'adapters')
GlobalRegistry.adapters = base
def clear_base():
    base.__init__(GlobalRegistry, 'adapters')

def test_deghostification_of_persistent_adapter_registries():
    """

We want to make sure that we see updates corrextly.

    >>> import persistent
    >>> import transaction
    >>> from zope.interface import Interface
    >>> from zope.interface import implements
    >>> class IFoo(Interface):
    ...     pass
    >>> class Foo(persistent.Persistent):
    ...     implements(IFoo)
    ...     name = ''
    ...     def __init__(self, name=''):
    ...         self.name = name
    ...     def __repr__(self):
    ...         return 'Foo(%r)' % self.name

    >>> from zope.component.testing import setUp, tearDown
    >>> setUp()
    >>> len(base._v_subregistries)
    0

    >>> import ZODB.tests.util
    >>> db = ZODB.tests.util.DB()
    >>> tm1 = transaction.TransactionManager()
    >>> c1 = db.open(transaction_manager=tm1)
    >>> from zope.component.persistentregistry import PersistentAdapterRegistry
    >>> r1 = PersistentAdapterRegistry((base,))
    >>> r2 = PersistentAdapterRegistry((r1,))
    >>> c1.root()[1] = r1
    >>> c1.root()[2] = r2
    >>> tm1.commit()
    >>> r1._p_deactivate()

    >>> len(base._v_subregistries)
    0

    >>> tm2 = transaction.TransactionManager()
    >>> c2 = db.open(transaction_manager=tm2)
    >>> r1 = c2.root()[1]
    >>> r2 = c2.root()[2]

    >>> r1.lookup((), IFoo, '')

    >>> base.register((), IFoo, '', Foo(''))
    >>> r1.lookup((), IFoo, '')
    Foo('')

    >>> r2.lookup((), IFoo, '1')

    >>> r1.register((), IFoo, '1', Foo('1'))

    >>> r2.lookup((), IFoo, '1')
    Foo('1')

    >>> r1.lookup((), IFoo, '2')
    >>> r2.lookup((), IFoo, '2')

    >>> base.register((), IFoo, '2', Foo('2'))

    >>> r1.lookup((), IFoo, '2')
    Foo('2')

    >>> r2.lookup((), IFoo, '2')
    Foo('2')

Cleanup:

    >>> db.close()
    >>> clear_base()
    >>> tearDown()
    """


def test_suite():
    import doctest
    return unittest.TestSuite((
        doctest.DocTestSuite(setUp=setUp, tearDown=tearDown),
        ))
