zope.introspectorui
*******************

UI components for the zope.introspector

:Test-Layer: functional

The ``zope.introspectorui`` provides UI components, mainly views, to
display informations digged by ``zope.introspector``.

Instances
=========

We create a class and an instance of that class, that we can lookup
afterwards::
  
  >>> from zope import interface
  >>> class Test(object):
  ...     interface.implements(interface.Interface)
  >>> test_instance = Test()

We look up the object info for the test object. The object info is
provided by ``zope.introspector``::
  
  >>> from zope import component
  >>> from zope.introspector.interfaces import IObjectInfo
  >>> object_info = component.getAdapter(test_instance, IObjectInfo, 
  ...                                    name='object')

Now we want to get some view for the object info obtained. This is the
job of ``zope.introspectorui``. We get a view for the instance defined
above::

  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()
  >>> view = component.getMultiAdapter((object_info, request), 
  ...                                  name='index.html')

We can render the view::  

  >>> print view()
  <table>...
  ...Type:...Test...
  ...Class:...__builtin__.Test...
  ...File:...builtin...
  

Packages
========

Packages also have information objects, so adapt this package, and
render that view:

  >>> import zope.introspectorui
  >>> from zope.introspector.interfaces import IPackageInfo
  >>> package_info = component.getAdapter(zope.introspectorui, IPackageInfo,
  ...                                     name='package')
  >>> view = component.getMultiAdapter((package_info, request), 
  ...                                  name='index.html')
  >>> print view()
  <h1>...Package: <span>zope.introspectorui</span>...
