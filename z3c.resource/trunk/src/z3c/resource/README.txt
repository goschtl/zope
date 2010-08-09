======
README
======

A IResource is a container located in a object annotation providing a 
container which contains IResourceItem. A resource item can be a file or
a image implementation marked with a IResourceItem interface. Such resource
items can get ``local`` traversed via the ``++resource++`` namespace. 
Let's show how this works:

  >>> from z3c.resource import interfaces
  >>> from z3c.resource.resource import Resource
  >>> res = Resource()
  >>> interfaces.IResource.providedBy(res)
  True

For the next test, we define a contant object providing IResourceTraversable:

  >>> import zope.interface
  >>> from zope.annotation import IAttributeAnnotatable
  >>> from zope.annotation.attribute import AttributeAnnotations
  >>> zope.component.provideAdapter(AttributeAnnotations)
  >>> class Content(object):
  ...     zope.interface.implements(interfaces.IResourceTraversable,
  ...                               IAttributeAnnotatable)

  >>> content = Content()

Such IResourceTraversable object can get adapted to IResource:

  >>> import zope.component
  >>> from z3c.resource.adapter import getResource
  >>> zope.component.provideAdapter(getResource)
  >>> res = interfaces.IResource(content)
  >>> res
  <z3c.resource.resource.Resource object at ...>

  >>> len(res)
  0

We can add a IResourceItem to this resource:

  >>> class Item(object):
  ...     zope.interface.implements(interfaces.IResourceItem)
  >>> item = Item()
  >>> res['item'] = item
  >>> len(res)
  1

There is also a namespace which makes the resource item traversable on 
the content object:

  >>> from z3c.resource.namespace import resource as resourceNamspace
  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()
  >>> traverser = resourceNamspace(content, request)

We can traverse to the IResource:

  >>> traverser.traverse(None, None)
  <z3c.resource.resource.Resource object at ...>

  >>> traverser.traverse(None, None).__parent__ is content
  True

  >>> traverser.traverse(None, None).__name__ == u'++resource++'
  True

And we can traverse to the resource item by its name:

  >>> traverser.traverse('item', None)
  <Item object at ...>
