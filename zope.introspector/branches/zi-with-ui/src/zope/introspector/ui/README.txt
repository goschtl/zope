  :Test-Layer: functional
  
  # Create a class and object for testing:
  >>> from zope import interface
  >>> class Test(object):
  ...     interface.implements(interface.Interface)
  >>> test_instance = Test()
  
  # Look up the object info for the test object:
  >>> from zope import component
  >>> from zope.introspector.interfaces import IObjectInfo
  >>> object_info = component.getAdapter(test_instance, IObjectInfo, 
  ...                                    name='object')
  
  # Find the view for the test object:
  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()
  >>> view = component.getMultiAdapter((object_info, request), 
  ...                                  name='index.html')
  
  # Try to render the view:
  >>> print view()
  <table>...
  ...Type:...Test...
  ...Class:...__builtin__.Test...
  ...File:...builtin...
  
  # Packages also have information objects, so adapt this package, and
  # render that view:
  >>> import zope.introspectorui
  >>> from zope.introspector.interfaces import IPackageInfo
  >>> package_info = component.getAdapter(zope.introspectorui, IPackageInfo,
  ...                                     name='package')
  >>> view = component.getMultiAdapter((package_info, request), name='index.html')
  >>> print view()
  <h1>...Package: <span>zope.introspectorui</span>...
