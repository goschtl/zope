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
"""Local Adapter Tests

   Local surrogates and surrogate registries share declarations with
   those "above" them.

   Suppose we have a global AdapterRegistry:

   >>> G = AdapterRegistry()

   we also have a local surrogate registry, with G as it's base:

   >>> L1 = LocalAdapterRegistry(G)

   and so on:

   >>> L2 = LocalAdapterRegistry(G, L1)

   Now, if we declare an adapter globally:

   >>> G.provideAdapter(IF1, IB1, [A11G])

   we can query it locally:

   >>> f2 = F2()

   >>> a = L1.queryAdapter(f2, IB1)
   >>> a.__class__.__name__
   'A11G'
   >>> a.args == (f2, )
   True

   >>> a = L2.queryAdapter(f2, IB1)
   >>> a.__class__.__name__
   'A11G'
   >>> a.args == (f2, )
   True

   We can add local definitions:

   >>> ra011 = Registration(required = IF0, provided=IB1, factory=A011)
   >>> L1.createRegistrationsFor(ra011).activate(ra011)

   and use it:

   >>> f0 = F0()

   >>> a = L1.queryAdapter(f0, IB1)
   >>> a.__class__.__name__
   'A011'
   >>> a.args == (f0, )
   True

   >>> a = L2.queryAdapter(f0, IB1)
   >>> a.__class__.__name__
   'A011'
   >>> a.args == (f0, )
   True

   but not outside L1:

   >>> G.queryAdapter(f0, IB1)

   Note that it doesn't override the non-local adapter:

   >>> a = L1.queryAdapter(f2, IB1)
   >>> a.__class__.__name__
   'A11G'
   >>> a.args == (f2, )
   True

   >>> a = L2.queryAdapter(f2, IB1)
   >>> a.__class__.__name__
   'A11G'
   >>> a.args == (f2, )
   True

   because it was more specific.

   Let's override the adapter in L2:

   >>> ra112 = Registration(required = IF1, provided=IB1, factory=A112)
   >>> L2.createRegistrationsFor(ra112).activate(ra112)

   Now, in L2, we get the new adapter, because it's as specific and more
   local than the one from G:

   >>> a = L2.queryAdapter(f2, IB1)
   >>> a.__class__.__name__
   'A112'
   >>> a.args == (f2, )
   True

   But we still get thye old one in L1

   >>> a = L1.queryAdapter(f2, IB1)
   >>> a.__class__.__name__
   'A11G'
   >>> a.args == (f2, )
   True

   Note that we can ask for less specific interfaces and still get the adapter:

   >>> a = L2.queryAdapter(f2, IB0)
   >>> a.__class__.__name__
   'A112'
   >>> a.args == (f2, )
   True

   >>> a = L1.queryAdapter(f2, IB0)
   >>> a.__class__.__name__
   'A11G'
   >>> a.args == (f2, )
   True

   We get the more specific adapter even if there is a less-specific
   adapter to B0:

   >>> G.provideAdapter(IF1, IB1, [A10G])

   >>> a = L2.queryAdapter(f2, IB0)
   >>> a.__class__.__name__
   'A112'
   >>> a.args == (f2, )
   True

   But if we have an equally specific and equally local adapter to B0, it
   will win:

   >>> ra102 = Registration(required = IF1, provided=IB0, factory=A102)
   >>> L2.createRegistrationsFor(ra102).activate(ra102)

   >>> a = L2.queryAdapter(f2, IB0)
   >>> a.__class__.__name__
   'A102'
   >>> a.args == (f2, )
   True

   We can deactivate registrations, which has the effect of deleting adapters:


   >>> L2.queryRegistrationsFor(ra112).deactivate(ra112)

   >>> a = L2.queryAdapter(f2, IB0)
   >>> a.__class__.__name__
   'A102'
   >>> a.args == (f2, )
   True

   >>> a = L2.queryAdapter(f2, IB1)
   >>> a.__class__.__name__
   'A10G'
   >>> a.args == (f2, )
   True

   >>> L2.queryRegistrationsFor(ra102).deactivate(ra102)

   >>> a = L2.queryAdapter(f2, IB0)
   >>> a.__class__.__name__
   'A10G'
   >>> a.args == (f2, )
   True

   $Id: tests.py,v 1.2 2004/03/13 15:21:07 srichter Exp $
   """

def test_named_adapters():
    """
    Suppose we have a global AdapterRegistry:

    >>> G = AdapterRegistry()

    we also have a local surrogate registry, with G as it's base:

    >>> L1 = LocalAdapterRegistry(G)

    and so on:

    >>> L2 = LocalAdapterRegistry(G, L1)

    Now, if we declare an adapter globally:

    >>> G.provideAdapter(IF1, IB1, [A11G], name='bob')

    we can query it locally:

    >>> f2 = F2()

    >>> L1.queryAdapter(f2, IB1)
    >>> a = L1.queryNamedAdapter(f2, IB1, 'bob')
    >>> a.__class__.__name__
    'A11G'
    >>> a.args == (f2, )
    True

    >>> L2.queryAdapter(f2, IB1)
    >>> a = L2.queryNamedAdapter(f2, IB1, 'bob')
    >>> a.__class__.__name__
    'A11G'
    >>> a.args == (f2, )
    True

    We can add local definitions:

    >>> ra011 = Registration(required = IF0, provided=IB1, factory=A011,
    ...                      name='bob')
    >>> L1.createRegistrationsFor(ra011).activate(ra011)
    
    and use it:

    >>> f0 = F0()

    >>> L1.queryAdapter(f0, IB1)
    >>> a = L1.queryNamedAdapter(f0, IB1, 'bob')
    >>> a.__class__.__name__
    'A011'
    >>> a.args == (f0, )
    True

    >>> L2.queryAdapter(f0, IB1)
    >>> a = L2.queryNamedAdapter(f0, IB1, 'bob')
    >>> a.__class__.__name__
    'A011'
    >>> a.args == (f0, )
    True

    but not outside L1:

    >>> G.queryNamedAdapter(f0, IB1, 'bob')

    Note that it doesn't override the non-local adapter:

    >>> L1.queryAdapter(f2, IB1)
    >>> a = L1.queryNamedAdapter(f2, IB1, 'bob')
    >>> a.__class__.__name__
    'A11G'
    >>> a.args == (f2, )
    True

    >>> L2.queryAdapter(f2, IB1)
    >>> a = L2.queryNamedAdapter(f2, IB1, 'bob')
    >>> a.__class__.__name__
    'A11G'
    >>> a.args == (f2, )
    True

    because it was more specific.

    Let's override the adapter in L2:

    >>> ra112 = Registration(required = IF1, provided=IB1, factory=A112,
    ...                      name='bob')
    >>> L2.createRegistrationsFor(ra112).activate(ra112)

    Now, in L2, we get the new adapter, because it's as specific and more
    local than the one from G:

    >>> L2.queryAdapter(f2, IB1)
    >>> a = L2.queryNamedAdapter(f2, IB1, 'bob')
    >>> a.__class__.__name__
    'A112'
    >>> a.args == (f2, )
    True

    But we still get thye old one in L1

    >>> L1.queryAdapter(f2, IB1)
    >>> a = L1.queryNamedAdapter(f2, IB1, 'bob')
    >>> a.__class__.__name__
    'A11G'
    >>> a.args == (f2, )
    True

    Note that we can ask for less specific interfaces and still get the adapter:

    >>> L2.queryAdapter(f2, IB0)
    >>> a = L2.queryNamedAdapter(f2, IB0, 'bob')
    >>> a.__class__.__name__
    'A112'
    >>> a.args == (f2, )
    True

    >>> L1.queryAdapter(f2, IB0)
    >>> a = L1.queryNamedAdapter(f2, IB0, 'bob')
    >>> a.__class__.__name__
    'A11G'
    >>> a.args == (f2, )
    True

    We get the more specific adapter even if there is a less-specific
    adapter to B0:

    >>> G.provideAdapter(IF1, IB1, [A10G], name='bob')

    >>> L2.queryAdapter(f2, IB0)
    >>> a = L2.queryNamedAdapter(f2, IB0, 'bob')
    >>> a.__class__.__name__
    'A112'
    >>> a.args == (f2, )
    True

    But if we have an equally specific and equally local adapter to B0, it
    will win:

    >>> ra102 = Registration(required = IF1, provided=IB0, factory=A102,
    ...                      name='bob')
    >>> L2.createRegistrationsFor(ra102).activate(ra102)
    
    >>> L2.queryAdapter(f2, IB0)
    >>> a = L2.queryNamedAdapter(f2, IB0, 'bob')
    >>> a.__class__.__name__
    'A102'
    >>> a.args == (f2, )
    True

    We can deactivate registrations, which has the effect of deleting adapters:


    >>> L2.queryRegistrationsFor(ra112).deactivate(ra112)

    >>> L2.queryAdapter(f2, IB0)
    >>> a = L2.queryNamedAdapter(f2, IB0, 'bob')
    >>> a.__class__.__name__
    'A102'
    >>> a.args == (f2, )
    True

    >>> L2.queryAdapter(f2, IB1)
    >>> a = L2.queryNamedAdapter(f2, IB1, 'bob')
    >>> a.__class__.__name__
    'A10G'
    >>> a.args == (f2, )
    True

    >>> L2.queryRegistrationsFor(ra102).deactivate(ra102)

    >>> L2.queryAdapter(f2, IB0)
    >>> a = L2.queryNamedAdapter(f2, IB0, 'bob')
    >>> a.__class__.__name__
    'A10G'
    >>> a.args == (f2, )
    True
    """

def test_multi_adapters():
    """
    Suppose we have a global AdapterRegistry:

    >>> G = AdapterRegistry()

    we also have a local surrogate registry, with G as it's base:

    >>> L1 = LocalAdapterRegistry(G)

    and so on:

    >>> L2 = LocalAdapterRegistry(G, L1)

    Now, if we declare an adapter globally:

    >>> G.provideAdapter(IF1, IB1, [A11G], name='bob', with=(IR0,))

    we can query it locally:

    >>> f2 = F2()
    >>> r = R1()

    >>> a = L1.queryMultiAdapter((f2, r), IB1, 'bob')
    >>> a.__class__.__name__
    'A11G'
    >>> a.args == (f2, r)
    True

    >>> a = L2.queryMultiAdapter((f2, r), IB1, 'bob')
    >>> a.__class__.__name__
    'A11G'
    >>> a.args == (f2, r)
    True

    We can add local definitions:

    >>> ra011 = Registration(required = IF0, provided=IB1, factory=A011,
    ...                      name='bob', with=(IR0,))
    >>> L1.createRegistrationsFor(ra011).activate(ra011)
    
    and use it:

    >>> f0 = F0()

    >>> a = L1.queryMultiAdapter((f0, r), IB1, 'bob')
    >>> a.__class__.__name__
    'A011'
    >>> a.args == (f0, r)
    True

    >>> a = L2.queryMultiAdapter((f0, r), IB1, 'bob')
    >>> a.__class__.__name__
    'A011'
    >>> a.args == (f0, r)
    True

    but not outside L1:

    >>> G.queryMultiAdapter((f0, r), IB1, 'bob')

    Note that it doesn't override the non-local adapter:

    >>> a = L1.queryMultiAdapter((f2, r), IB1, 'bob')
    >>> a.__class__.__name__
    'A11G'
    >>> a.args == (f2, r)
    True

    >>> a = L2.queryMultiAdapter((f2, r), IB1, 'bob')
    >>> a.__class__.__name__
    'A11G'
    >>> a.args == (f2, r)
    True

    because it was more specific.

    Let's override the adapter in L2:

    >>> ra112 = Registration(required = IF1, provided=IB1, factory=A112,
    ...                      name='bob', with=(IR0,))
    >>> L2.createRegistrationsFor(ra112).activate(ra112)

    Now, in L2, we get the new adapter, because it's as specific and more
    local than the one from G:

    >>> a = L2.queryMultiAdapter((f2, r), IB1, 'bob')
    >>> a.__class__.__name__
    'A112'
    >>> a.args == (f2, r)
    True

    But we still get the old one in L1

    >>> a = L1.queryMultiAdapter((f2, r), IB1, 'bob')
    >>> a.__class__.__name__
    'A11G'
    >>> a.args == (f2, r)
    True

    Note that we can ask for less specific interfaces and still get
    the adapter:

    >>> a = L2.queryMultiAdapter((f2, r), IB0, 'bob')
    >>> a.__class__.__name__
    'A112'
    >>> a.args == (f2, r)
    True

    >>> a = L1.queryMultiAdapter((f2, r), IB0, 'bob')
    >>> a.__class__.__name__
    'A11G'
    >>> a.args == (f2, r)
    True

    We get the more specific adapter even if there is a less-specific
    adapter to B0:

    >>> G.provideAdapter(IF1, IB1, [A10G], name='bob', with=(IR0,))

    >>> a = L2.queryMultiAdapter((f2, r), IB0, 'bob')
    >>> a.__class__.__name__
    'A112'
    >>> a.args == (f2, r)
    True

    But if we have an equally specific and equally local adapter to B0, it
    will win:

    >>> ra102 = Registration(required = IF1, provided=IB0, factory=A102,
    ...                      name='bob', with=(IR0,))
    >>> L2.createRegistrationsFor(ra102).activate(ra102)
    
    >>> a = L2.queryMultiAdapter((f2, r), IB0, 'bob')
    >>> a.__class__.__name__
    'A102'
    >>> a.args == (f2, r)
    True

    We can deactivate registrations, which has the effect of deleting adapters:

    >>> L2.queryRegistrationsFor(ra112).deactivate(ra112)

    >>> a = L2.queryMultiAdapter((f2, r), IB0, 'bob')
    >>> a.__class__.__name__
    'A102'
    >>> a.args == (f2, r)
    True

    >>> a = L2.queryMultiAdapter((f2, r), IB1, 'bob')
    >>> a.__class__.__name__
    'A10G'
    >>> a.args == (f2, r)
    True

    >>> L2.queryRegistrationsFor(ra102).deactivate(ra102)

    >>> L2.queryAdapter(f2, IB0)
    >>> a = L2.queryMultiAdapter((f2, r), IB0, 'bob')
    >>> a.__class__.__name__
    'A10G'
    >>> a.args == (f2, r)
    True
    """

def test_persistence():
    """
    >>> db = DB()
    >>> conn1 = db.open()

    >>> G = globalAdapterRegistry
    >>> L1 = LocalAdapterRegistry(G)
    >>> L2 = LocalAdapterRegistry(G, L1)

    >>> conn1.root()['L1'] = L1
    >>> conn1.root()['L2'] = L2
    
    >>> G.provideAdapter(IF1, IB1, [A11G], name='bob')
    >>> f2 = F2()
    >>> L1.queryAdapter(f2, IB1)
    >>> a = L1.queryNamedAdapter(f2, IB1, 'bob')
    >>> a.__class__.__name__
    'A11G'
    >>> a.args == (f2, )
    True

    >>> L2.queryAdapter(f2, IB1)
    >>> a = L2.queryNamedAdapter(f2, IB1, 'bob')
    >>> a.__class__.__name__
    'A11G'
    >>> a.args == (f2, )
    True

    We can add local definitions:

    >>> ra011 = Registration(required = IF0, provided=IB1, factory=A011,
    ...                      name='bob')
    >>> L1.createRegistrationsFor(ra011).activate(ra011)

    and use it:

    >>> f0 = F0()

    >>> L1.queryAdapter(f0, IB1)
    >>> a = L1.queryNamedAdapter(f0, IB1, 'bob')
    >>> a.__class__.__name__
    'A011'
    >>> a.args == (f0, )
    True

    >>> L2.queryAdapter(f0, IB1)
    >>> a = L2.queryNamedAdapter(f0, IB1, 'bob')
    >>> a.__class__.__name__
    'A011'
    >>> a.args == (f0, )
    True

    but not outside L1:

    >>> G.queryAdapter(f0, IB1)

    Note that it doesn't override the non-local adapter:

    >>> L1.queryAdapter(f2, IB1)
    >>> a = L1.queryNamedAdapter(f2, IB1, 'bob')
    >>> a.__class__.__name__
    'A11G'
    >>> a.args == (f2, )
    True

    >>> L2.queryAdapter(f2, IB1)
    >>> a = L2.queryNamedAdapter(f2, IB1, 'bob')
    >>> a.__class__.__name__
    'A11G'
    >>> a.args == (f2, )
    True

    because it was more specific.

    Let's override the adapter in L2:

    >>> ra112 = Registration(required = IF1, provided=IB1, factory=A112,
    ...                      name='bob')
    >>> L2.createRegistrationsFor(ra112).activate(ra112)

    Now, in L2, we get the new adapter, because it's as specific and more
    local than the one from G:

    >>> L2.queryAdapter(f2, IB1)
    >>> a = L2.queryNamedAdapter(f2, IB1, 'bob')
    >>> a.__class__.__name__
    'A112'
    >>> a.args == (f2, )
    True

    But we still get the old one in L1

    >>> L1.queryAdapter(f2, IB1)
    >>> a = L1.queryNamedAdapter(f2, IB1, 'bob')
    >>> a.__class__.__name__
    'A11G'
    >>> a.args == (f2, )
    True

    Note that we can ask for less specific interfaces and still get the adapter:

    >>> L2.queryAdapter(f2, IB0)
    >>> a = L2.queryNamedAdapter(f2, IB0, 'bob')
    >>> a.__class__.__name__
    'A112'
    >>> a.args == (f2, )
    True

    >>> L1.queryAdapter(f2, IB0)
    >>> a = L1.queryNamedAdapter(f2, IB0, 'bob')
    >>> a.__class__.__name__
    'A11G'
    >>> a.args == (f2, )
    True

    We get the more specific adapter even if there is a less-specific
    adapter to B0:

    >>> G.provideAdapter(IF0, IB0, [A00G], name='bob')

    >>> L2.queryAdapter(f2, IB0)
    >>> a = L2.queryNamedAdapter(f2, IB0, 'bob')
    >>> a.__class__.__name__
    'A112'
    >>> a.args == (f2, )
    True

    But if we have an equally specific and equally local adapter to B0, it
    will win:

    >>> ra102 = Registration(required = IF1, provided=IB0, factory=A102,
    ...                      name='bob')
    >>> L2.createRegistrationsFor(ra102).activate(ra102)

    >>> L2.queryAdapter(f2, IB0)
    >>> a = L2.queryNamedAdapter(f2, IB0, 'bob')
    >>> a.__class__.__name__
    'A102'
    >>> a.args == (f2, )
    True

    >>> L1.queryNamedAdapter(f2, IB0, 'bob').__class__.__name__
    'A11G'
    >>> L1.queryNamedAdapter(f2, IB1, 'bob').__class__.__name__
    'A11G'
    >>> L2.queryNamedAdapter(f2, IB0, 'bob').__class__.__name__
    'A102'
    >>> L2.queryNamedAdapter(f2, IB1, 'bob').__class__.__name__
    'A112'

    >>> get_transaction().commit()

    Now, let's open another transaction:

    >>> conn2 = db.open()

    >>> L1 = conn2.root()['L1']
    >>> L2 = conn2.root()['L2']

    We should get the same outputs:

    >>> L1.queryNamedAdapter(f2, IB0, 'bob').__class__.__name__
    'A11G'
    >>> L1.queryNamedAdapter(f2, IB1, 'bob').__class__.__name__
    'A11G'
    >>> L2.queryNamedAdapter(f2, IB0, 'bob').__class__.__name__
    'A102'
    >>> L2.queryNamedAdapter(f2, IB1, 'bob').__class__.__name__
    'A112'
    
    We can deactivate registrations, which has the effect of deleting adapters:

    >>> L2.queryRegistrationsFor(ra112).deactivate(ra112)
    >>> L2.queryRegistrationsFor(ra102).deactivate(ra102)

    >>> L1.queryNamedAdapter(f2, IB0, 'bob').__class__.__name__
    'A11G'
    >>> L1.queryNamedAdapter(f2, IB1, 'bob').__class__.__name__
    'A11G'
    >>> L2.queryNamedAdapter(f2, IB0, 'bob').__class__.__name__
    'A11G'
    >>> L2.queryNamedAdapter(f2, IB1, 'bob').__class__.__name__
    'A11G'

    >>> get_transaction().commit()

    If we look back at the first connection, we should get the same data:

    >>> conn1.sync()
    >>> L1 = conn1.root()['L1']
    >>> L2 = conn1.root()['L2']

    We should see the result of the deactivations:
    
    >>> L1.queryNamedAdapter(f2, IB0, 'bob').__class__.__name__
    'A11G'
    >>> L1.queryNamedAdapter(f2, IB1, 'bob').__class__.__name__
    'A11G'
    >>> L2.queryNamedAdapter(f2, IB0, 'bob').__class__.__name__
    'A11G'
    >>> L2.queryNamedAdapter(f2, IB1, 'bob').__class__.__name__
    'A11G'

    Cleanup:
    >>> G.__init__()
    >>> db.close()
    """


def test_local_default():
    """
    >>> G = AdapterRegistry()
    >>> L1 = LocalAdapterRegistry(G)
    >>> r = Registration(required = None, provided=IB1, factory=Adapter)
    >>> L1.createRegistrationsFor(r).activate(r)
    >>> f2 = F2()
    >>> L1.queryAdapter(f2, IB1).__class__.__name__
    'Adapter'
    """


def test_changing_next():
    """
    >>> G = AdapterRegistry()
    >>> L1 = LocalAdapterRegistry(G)
    >>> L2 = LocalAdapterRegistry(G, L1)
    >>> f2 = F2()

    >>> L2.queryAdapter(f2, IB1).__class__.__name__
    'NoneType'

    >>> G.provideAdapter(IF1, IB1, [A11G])
    >>> L2.queryAdapter(f2, IB1).__class__.__name__
    'A11G'


    >>> class A111(Adapter):
    ...     pass
    >>> ra111 = Registration(required = IF1, provided=IB1, factory=A111)
    >>> L1.createRegistrationsFor(ra111).activate(ra111)
    >>> L2.queryAdapter(f2, IB1).__class__.__name__
    'A111'

    >>> L1.next
    >>> L2.next == L1
    True
    >>> L1.subs == (L2,)
    True
    >>> L3 = LocalAdapterRegistry(G, L1)
    >>> L2.setNext(L3)
    >>> L2.next == L3
    True
    >>> L3.next == L1
    True
    >>> L1.subs == (L3,)
    True
    >>> L3.subs == (L2,)
    True

    >>> class A113(Adapter):
    ...     pass
    >>> ra113 = Registration(required = IF1, provided=IB1, factory=A113)
    >>> L3.createRegistrationsFor(ra113).activate(ra113)

    >>> L2.queryAdapter(f2, IB1).__class__.__name__
    'A113'
    >>> L2.setNext(L1)
    >>> L2.next == L1
    True
    >>> L3.next == L1
    True
    >>> L1.subs == (L3, L2)
    True
    >>> L3.subs == ()
    True
    >>> L2.queryAdapter(f2, IB1).__class__.__name__
    'A111'

    """

def test_LocalAdapterBasedService():
    """
    Setup folders and service managers:
    
    >>> from zope.app.tests import setup
    >>> setup.placefulSetUp()
    >>> root = setup.buildSampleFolderTree()
    >>> sm = setup.createServiceManager(root)
    >>> sm1 = setup.createServiceManager(root['folder1'])
    >>> sm1_1 = setup.createServiceManager(root['folder1']['folder1_1'])
    >>> sm1_1_1 = setup.createServiceManager(
    ...                         root['folder1']['folder1_1']['folder1_1_1'])

    Define the service

    >>> gsm = zapi.getServiceManager(None)
    >>> gsm.defineService('F', IF1)

    Create the global service

    >>> g = F2()
    >>> gsm.provideService('F', g)

    Create a local service class, which must define setNext:

    >>> import zope.app.site.interfaces
    >>> class LocalF(LocalAdapterBasedService):
    ...     zope.interface.implements(
    ...         IF2,
    ...         zope.app.site.interfaces.ISimpleService,
    ...         )
    ...     def setNext(self, next, global_):
    ...         self.next, self.global_ = next, global_

    If we add a local service, It gets it's next and global_ attrs set:

    >>> f1 = LocalF()
    >>> hasattr(f1, 'next') or hasattr(f1, 'global_')
    False
    >>> setup.addService(sm1, 'F', f1) is f1
    True
    >>> (f1.next, f1.global_) == (None, g)
    True

    If we add another service below, it's next will point to the one
    above:
    
    >>> f1_1_1 = LocalF()
    >>> setup.addService(sm1_1_1, 'F', f1_1_1) is f1_1_1
    True
    >>> (f1_1_1.next, f1_1_1.global_) == (f1, g)
    True

    We can insert a service in an intermediate site:
    
    >>> f1_1 = LocalF()
    >>> setup.addService(sm1_1, 'F', f1_1) is f1_1
    True
    >>> (f1_1.next, f1_1.global_) == (f1, g)
    True
    >>> (f1_1_1.next, f1_1_1.global_) == (f1_1, g)
    True

    Deactivating services adjust the relevant next pointers

    >>> default = zapi.traverse(sm1_1, 'default')
    >>> rm = default.getRegistrationManager()
    >>> rm.values()[0].status = RegisteredStatus
    >>> (f1_1_1.next, f1_1_1.global_) == (f1, g)
    True

    >>> default = zapi.traverse(sm1, 'default')
    >>> rm = default.getRegistrationManager()
    >>> rm.values()[0].status = RegisteredStatus
    >>> (f1_1_1.next, f1_1_1.global_) == (None, g)
    True
    
    >>> setup.placefulTearDown()
    """



import unittest
from zope.testing.doctestunit import DocTestSuite
from zope.interface.adapter import AdapterRegistry
from zope.app.adapter.adapter import LocalAdapterRegistry
from zope.app.adapter.adapter import LocalAdapterBasedService
import zope.interface
from ZODB.tests.util import DB
from transaction import get_transaction
from zope.app import zapi
from zope.app.interfaces.services.registration import RegisteredStatus

class IF0(zope.interface.Interface):
    pass

class IF1(IF0):
    pass

class IF2(IF1):
    pass

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

class F0:
    zope.interface.implements(IF0)

class F2:
    zope.interface.implements(IF2)

class Adapter:
    def __init__(self, *args):
        self.args = args

class A00G(Adapter):
    pass

class A11G(Adapter):
    pass

class A112(Adapter):
    pass

class A10G(Adapter):
    pass

class A102(Adapter):
    pass

class A011(Adapter):
    pass

class Registration:
    name=u''
    with=()
    provided=zope.interface.Interface
    required=None
    
    def __init__(self, **kw):
        self.__dict__.update(kw)

    def __repr__(self):
        return "<Registration %s>" % self.__dict__

    def factories(self):
        return self.factory,
    factories = property(factories)

# Create a picklable global registry. The pickleability of other
# global surrogate registries is beyond the scope of these tests:
class GlobalAdapterRegistry(AdapterRegistry):
    def __reduce__(self):
        return 'globalAdapterRegistry'

globalAdapterRegistry = GlobalAdapterRegistry()

class TestStack:
    registration = None

    def __init__(self, parent):
        self.__parent__ = parent

    def activate(self, registration):
        self.registration = registration
        self.__parent__.notifyActivated(self, registration)

    def deactivate(self, registration):
        self.registration = None
        self.__parent__.notifyDeactivated(self, registration)

    def active(self):
        return self.registration
    

class LocalAdapterRegistry(LocalAdapterRegistry):
    """For testing, use custom stack type
    """
    _stackType = TestStack
    

def test_suite():
    return unittest.TestSuite((
        DocTestSuite(),
        ))

if __name__ == '__main__': unittest.main()
