=========
z3c.proxy
=========

We can proxy a regular container derived from zope's btree container for
example:

  >>> from zope.container.interfaces import IContainer
  >>> from zope.container.btree import BTreeContainer
  >>> container = BTreeContainer()
  >>> container.__name__, container.__parent__ = u'c1', u'p1'

  >>> from z3c.proxy import interfaces
  >>> from z3c.proxy.container import LocationProxy
  >>> from z3c.proxy.container import ContainerLocationProxy
  >>> proxy = ContainerLocationProxy(container)

The name and the parent of the proxy is None. The proxy provides
IContainer:

  >>> proxy.__name__ is None
  True
  >>> proxy.__parent__ is None
  True
  >>> IContainer.providedBy(proxy)
  True
  >>> interfaces.IContainerLocationProxy.providedBy(proxy)
  True

First we check the empty proxy:

  >>> proxy['x']
  Traceback (most recent call last):
  ...
  KeyError: 'x'

  >>> 'x' in proxy
  False

  >>> proxy.has_key('x')
  0

  >>> [key for key in proxy.keys()]
  []

  >>> [item for item in proxy.items()]
  []

  >>> proxy.get('x') is None
  True

  >>> iterator = iter(proxy)
  >>> iterator.next()
  Traceback (most recent call last):
  ...
  StopIteration

  >>> proxy.values()
  []

  >>> len(proxy)
  0

  >>> del proxy['x']
  Traceback (most recent call last):
  ...
  KeyError: 'x'

  >>> from zope.container.contained import Contained
  >>> proxy['x'] = x = Contained()

Now we added our first item. This item should be added to the container.
Its name will be x and its parent is the container itself:

  >>> x is container['x']
  True

  >>> x.__name__
  u'x'

  >>> x.__parent__ is container
  True

If we lookup 'x' within the proxy we do not get the blank 'x' but rather
the proxied 'x'. The proxy is not 'x' but only equal to 'x':

  >>> x is proxy['x']
  False

  >>> x == proxy['x']
  True

  >>> x1 = proxy['x']
  >>> from zope.proxy import isProxy
  >>> isProxy(x1)
  True

  >>> isinstance(x1, LocationProxy)
  True

The proxied 'x' has still the same name but not the same parent:

  >>> x1.__name__
  u'x'

  >>> x1.__parent__ is container
  False

  >>> x1.__parent__ is proxy
  True

If we add a second item to the container, it should appear in the
proxy, too. But this item is proxied as container location proxy:

  >>> container['y'] = y = BTreeContainer()
  >>> y1 = proxy['y']
  >>> y1 is y
  False

  >>> y1 == y
  True

  >>> isinstance(y1, ContainerLocationProxy)
  True

The container location proxy is able to proxy the location of
nested objects:

  >>> proxy['y']['z'] = z = Contained()
  >>> container['y']['z'] is z
  True

  >>> z1 = y1['z']
  >>> z1 is z
  False

  >>> z1 == z
  True

  >>> isinstance(z1, LocationProxy)
  True

  >>> z1.__parent__ is y1
  True

Finaly we check all other methods of the proxy:

  >>> 'x' in proxy
  True

  >>> proxy.has_key('x')
  1

  >>> keys = [key for key in proxy.keys()]; keys.sort(); keys
  [u'x', u'y']

  >>> items = [item for item in proxy.items()]; items.sort()
  >>> items == [(u'x', x), (u'y', y)]
  True

  >>> proxy.get('x') == x
  True

  >>> iterator = iter(proxy)
  >>> iterator.next() in proxy
  True

  >>> iterator.next() in proxy
  True

  >>> iterator.next()
  Traceback (most recent call last):
  ...
  StopIteration

  >>> values = proxy.values(); values.sort();
  >>> x in values, y in values
  (True, True)

  >>> len(proxy)
  2

  >>> del proxy['x']
  >>> 'x' in proxy
  False


ObjectMover
-----------

To use an object mover, pass a contained ``object`` to the class. The
contained ``object`` should implement ``IContained``.  It should be contained
in a container that has an adapter to ``INameChooser``.

Setup test container and proxies:

  >>> from zope.interface import implements
  >>> from zope.container.interfaces import INameChooser
  >>> from zope.copypastemove import ExampleContainer
  >>> from z3c.proxy.container import ProxyAwareObjectMover

  >>> class ContainerLocationProxyStub(ContainerLocationProxy):
  ...
  ...     implements(INameChooser)
  ...
  ...     def chooseName(self, name, ob):
  ...        while name in self:
  ...            name += '_'
  ...        return name

  >>> container = ExampleContainer()
  >>> container2 = ExampleContainer()

  >>> ob = Contained()
  >>> proxy = ContainerLocationProxyStub(container)
  >>> proxy[u'foo'] = ob
  >>> ob = proxy[u'foo']
  >>> mover = ProxyAwareObjectMover(ob)

In addition to moving objects, object movers can tell you if the object is
movable:

  >>> mover.moveable()
  1

which, at least for now, they always are.  A better question to ask is whether
we can move to a particular container. Right now, we can always move to a
container of the same class:

  >>> proxy2 = ContainerLocationProxyStub(container2)
  >>> mover.moveableTo(proxy2)
  1

  >>> mover.moveableTo({})
  Traceback (most recent call last):
  ...
  TypeError: Container is not a valid Zope container.

Of course, once we've decided we can move an object, we can use the mover to
do so:

  >>> mover.moveTo(proxy2)
  u'foo'

  >>> list(proxy)
  []

  >>> list(proxy2)
  [u'foo']

  >>> ob = proxy2[u'foo']
  >>> ob.__parent__ is proxy2
  True

We can also specify a name:

  >>> mover.moveTo(proxy2, u'bar')
  u'bar'

  >>> list(proxy2)
  [u'bar']

  >>> ob = proxy2[u'bar']
  >>> ob.__parent__ is proxy2
  True

  >>> ob.__name__
  u'bar'

But we may not use the same name given, if the name is already in use:

  >>> proxy2[u'splat'] = 1
  >>> mover.moveTo(proxy2, u'splat')
  u'splat_'

  >>> l = list(proxy2)
  >>> l.sort()
  >>> l
  [u'splat', u'splat_']

  >>> ob = proxy2[u'splat_']
  >>> ob.__name__
  u'splat_'

If we try to move to an invalid container, we'll get an error:

  >>> mover.moveTo({})
  Traceback (most recent call last):
  ...
  TypeError: Container is not a valid Zope container.


ObjectCopier
------------

To use an object copier, pass a contained ``object`` to the class. The
contained ``object`` should implement ``IContained``.  It should be contained
in a container that has an adapter to `INameChooser`.

Setup test container and proxies:

  >>> from z3c.proxy.container import ProxyAwareObjectCopier
  >>> class ContainerLocationProxyStub(ContainerLocationProxy):
  ...
  ...     implements(INameChooser)
  ...
  ...     def chooseName(self, name, ob):
  ...        while name in self:
  ...            name += '_'
  ...        return name


  >>> container = ExampleContainer()
  >>> container2 = ExampleContainer()

  >>> proxy = ContainerLocationProxyStub(container)
  >>> proxy[u'foo'] = ob = Contained()
  >>> ob = proxy[u'foo']
  >>> copier = ProxyAwareObjectCopier(ob)

In addition to moving objects, object copiers can tell you if the object is
movable:

  >>> copier.copyable()
  1

which, at least for now, they always are.  A better question to ask is whether
we can copy to a particular container. Right now, we can always copy to a
container of the same class:

  >>> proxy2 = ContainerLocationProxyStub(container2)
  >>> copier.copyableTo(proxy2)
  1

  >>> copier.copyableTo({})
  Traceback (most recent call last):
  ...
  TypeError: Container is not a valid Zope container.

Of course, once we've decided we can copy an object, we can use the copier to
do so:

  >>> copier.copyTo(proxy2)
  u'foo'

  >>> list(proxy)
  [u'foo']

  >>> list(proxy2)
  [u'foo']

  >>> ob.__parent__ is proxy
  1

  >>> proxy2[u'foo'] is ob
  0

  >>> proxy2[u'foo'].__parent__ is proxy2
  1

  >>> proxy2[u'foo'].__name__
  u'foo'

We can also specify a name:

  >>> copier.copyTo(proxy2, u'bar')
  u'bar'

  >>> l = list(proxy2)
  >>> l.sort()
  >>> l
  [u'bar', u'foo']

  >>> ob.__parent__ is proxy
  1

  >>> proxy2[u'bar'] is ob
  0

  >>> proxy2[u'bar'].__parent__ is proxy2
  1

  >>> proxy2[u'bar'].__name__
  u'bar'

But we may not use the same name given, if the name is already in use:

  >>> copier.copyTo(proxy2, u'bar')
  u'bar_'

  >>> l = list(proxy2)
  >>> l.sort()
  >>> l
  [u'bar', u'bar_', u'foo']

  >>> proxy2[u'bar_'].__name__
  u'bar_'


If we try to copy to an invalid container, we'll get an error:

  >>> copier.copyTo({})
  Traceback (most recent call last):
  ...
  TypeError: Container is not a valid Zope container.


ProxyAwareContainerItemRenamer
------------------------------

This adapter uses IObjectMover to move an item within the same container to
a different name. We need to first setup an adapter for IObjectMover:

Setup test container and proxies:

  >>> from zope.container.sample import SampleContainer
  >>> from zope.copypastemove import ContainerItemRenamer
  >>> from zope.copypastemove import IObjectMover
  >>> from z3c.proxy.container import ProxyAwareContainerItemRenamer

  >>> import zope.component
  >>> from zope.container.interfaces import IContained
  >>> zope.component.provideAdapter(ProxyAwareObjectMover, [IContained],
  ...     IObjectMover)

  >>> class ContainerLocationProxyStub(ContainerLocationProxy):
  ...
  ...     implements(INameChooser)
  ...
  ...     def chooseName(self, name, ob):
  ...        while name in self:
  ...            name += '_'
  ...        return name

To rename an item in a container, instantiate a ContainerItemRenamer with the
container:

  >>> container = SampleContainer()
  >>> proxy = ContainerLocationProxyStub(container)
  >>> renamer = ProxyAwareContainerItemRenamer(container)

For this example, we'll rename an item 'foo':

  >>> from z3c.proxy.container import _unproxy
  >>> foo = Contained()
  >>> proxy['foo'] = foo
  >>> proxy['foo'] == _unproxy(foo)
  True

to 'bar':

  >>> renamer.renameItem('foo', 'bar')
  >>> proxy['foo'] is foo
  Traceback (most recent call last):
  KeyError: 'foo'

  >>> proxy['bar'] == _unproxy(foo)
  True

If the item being renamed isn't in the container, a NotFoundError is raised:

  >>> renamer.renameItem('foo', 'bar') # doctest:+ELLIPSIS
  Traceback (most recent call last):
  ItemNotFoundError: (<...SampleContainer...>, 'foo')

If the new item name already exists, a DuplicationError is raised:

  >>> renamer.renameItem('bar', 'bar')
  Traceback (most recent call last):
  DuplicationError: bar is already in use
