======
README
======

The z3c.breadcrumb package provides base classes for breadcrumb
implementations. It allows you to write adapters for each content object which
provides it's own rule for providing the breadcrumb name, url and selection.

Let's do some imports we will use later.

  >>> import zope.interface
  >>> import zope.component
  >>> from zope.publisher.interfaces.http import IHTTPRequest
  >>> from zope.publisher.browser import TestRequest
  >>> from zope.traversing.browser import absoluteURL
  >>> from zope.app.container import contained
  >>> from z3c.breadcrumb import interfaces
  >>> from z3c.breadcrumb import browser


IBreadcrumb
-----------

Let's define a interface and a content object.

  >>> class IOffice(zope.interface.Interface):
  ...     """Office interface."""

  >>> class Office(contained.Contained):
  ...     zope.interface.implements(IOffice)
  ...     def __init__(self, label):
  ...         self.label = label
  ...         self.activeURL = True

  >>> office = Office(u'Zope Foundation')
  >>> office.__name__ = u'ZF'

There is a generic breadcrumb implementation which is registered by
default. If we do not implement a custom IBreadcrumb the generic adapter will
return the ``title`` or ``__name__`` of the item. Let's register the default
adapter, this is normaly done in ``configure.zcml``:

  >>> zope.component.provideAdapter(browser.GenericBreadcrumb)

And see what we get:

  >>> request = TestRequest()
  >>> breadcrumb = zope.component.getMultiAdapter((office, request),
  ...     interfaces.IBreadcrumb)
  >>> breadcrumb.name
  u'ZF'

We can also implement a custom ``IBreadcrumb`` adapter and provide another
name for the breadcrumb name:

  >>> class BreadcrumbForOffice(object):
  ...     zope.interface.implements(interfaces.IBreadcrumb)
  ...     zope.component.adapts(IOffice, IHTTPRequest)
  ...
  ...     def __init__(self, context, request):
  ...         self.context = context
  ...         self.request = request
  ...
  ...     @property
  ...     def name(self):
  ...         return self.context.label
  ...
  ...     @property
  ...     def url(self):
  ...         return absoluteURL(self.context, self.request)
  ...
  ...     @property
  ...     def activeURL(self):
  ...         return self.context.activeURL

Let's register the custom ``IBreadcrumb`` adapter for IOffice:

  >>> zope.component.provideAdapter(BreadcrumbForOffice)

And check the new breadcrumb name:

  >>> breadcrumb = zope.component.getMultiAdapter((office, request),
  ...     interfaces.IBreadcrumb)
  >>> breadcrumb.name
  u'Zope Foundation'


IBreadcrumbs
------------

There is also a IBreadcrumbs adapter which knows how to collect breadcrumb
informations for each item he traverses. We need to setup a little bit
infrastucture:

  >>> root = rootFolder
  >>> root['office'] = office

Register the IBreadcrumbs adapter:

  >>> zope.component.provideAdapter(browser.Breadcrumbs,
  ...     (zope.interface.Interface, zope.interface.Interface),
  ...     interfaces.IBreadcrumbs)


Now we can collect breadcrumbs for our items. You can see the url is correct
and the label ``Zope Foundation`` is collected by the custom IBreadcrumb
adapter:

  >>> breadcrumb = zope.component.getMultiAdapter((office, request),
  ...     interfaces.IBreadcrumbs)
  >>> list(breadcrumb.crumbs)
  [{'url': 'http://127.0.0.1',
    'activeURL': True,
    'name': 'top'},
   {'url': 'http://127.0.0.1/office',
    'activeURL': True,
    'name': u'Zope Foundation'}]
