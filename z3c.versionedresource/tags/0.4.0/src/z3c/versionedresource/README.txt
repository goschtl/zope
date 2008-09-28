===================
Versioned Resources
===================

When deploying scalable Web applications, it is important to serve all static
resources such as Javascript code, CSS, and images as quickly as possible
using as little resources as possible. On the hand, the resources must be
known within the application, so that they can be properly referenced.

Additionally, we want to set the expiration date as far in the future as
possible. However, sometimes we need or want to update a resource before the
expiration date has arrived. Yahoo has solved this problem by including a
version number into the URL, which then allowed them to set the expiration
date effectively to infinity.

However, maintaining the versions manually is a nightmare, since you would not
only need to change file or directory names all the time as you change them,
but also adjust your code. This package aims to solve this problem by
providing a central component to manage the versions of the resources and make
versioning transparent to the developer.


The Version Manager
-------------------

The Version Manager is a central component that provides the version to the
system. It is up to the version manager to decide whether the version is for
example based on a tag, a revision number, the package version number or a
manually entered version.

  >>> from z3c.versionedresource import version

This package provides only a simple version manager, since I have found no
other good version indicator that is available generically.

  >>> manager = version.VersionManager('1.0.0')
  >>> manager
  <VersionManager '1.0.0'>

The only constructor argument is the version itself. Versions must be ASCII
strings. Let's now register the version manager, so that it is available for
later use:

  >>> import zope.component
  >>> zope.component.provideUtility(manager)

Clearly, there is not much to version managers and they are only interesting
within the larger context of this package.


Versioned Resource Traversal
----------------------------

Zope uses a special, empty-named view to traverse resources from a site like
this::

  <site>/@@/<resource-path>

We would like to support URLs like this now::

  <site>/@@/<version>/<resource-path>

That means that we need a custom implementation of the resources view that can
handle the version.

  >>> from zope.publisher.browser import TestRequest
  >>> from z3c.versionedresource import resource

  >>> request = TestRequest()
  >>> context = object()

  >>> resources = resource.Resources(context, request)

The resources object is a browser view:

  >>> resources.__parent__ is context
  True
  >>> resources.__name__

The view is also a browser publisher. But it dows not support a default:

  >>> resources.browserDefault(request)
  (<function empty at ...>, ())

When traversing to a sub-item, the version can be specified:

  >>> resources.publishTraverse(request, '1.0.0')
  <zope.app.publisher.browser.resources.Resources ...>

The result of the traversal is the original resources object. When asking for
an unknown resource or version, a ``NotFound`` is raised:

  >>> resources.publishTraverse(request, 'error')
  Traceback (most recent call last):
  ...
  NotFound: Object: <z3c.versionedresource.resource.Resources ...>, name: 'error'

Let's now register a resource, just to show that traversing to it works:

  >>> import zope.interface
  >>> from zope.app.publisher.browser.resource import Resource

  >>> zope.component.provideAdapter(
  ...     Resource, (TestRequest,), zope.interface.Interface, 'resource.css')

We can now ask the resources object to traverse the resource:

  >>> css = resources.publishTraverse(request, 'resource.css')
  >>> css
  <zope.app.publisher.browser.resource.Resource object at ...>

Calling it will return the URL:

  >>> css()
  'http://127.0.0.1/@@/resource.css'

Mmmh, so a regular resource does not honor the version element. That's because
it's ``__call__()`` method defines how the URL is constructed, which is
ignorant of the version.

So let's use this package's implementation of a resource:

  >>> zope.component.provideAdapter(
  ...     resource.Resource,
  ...     (TestRequest,), zope.interface.Interface, 'resource2.css')

  >>> css = resources.publishTraverse(request, 'resource2.css')
  >>> css
  <z3c.versionedresource.resource.Resource object at ...>
  >>> css()
  'http://127.0.0.1/@@/1.0.0/resource2.css'


Custom Resource Classes
-----------------------

The ``zope.app.publisher.browser`` package defines three major
resources. As pointed out above, they have to be adjusted to produce a
versioned URL and set the cache header to a long time.

File Resource
~~~~~~~~~~~~~

The versioned file resource is identical to the default file resource, except
that it has a versioned URL and a 10 year cache timeout.

  >>> import os.path
  >>> import z3c.versionedresource.tests
  >>> filesdir = os.path.join(
  ...     os.path.dirname(z3c.versionedresource.tests.__file__),
  ...     'testfiles')

  >>> from zope.app.publisher.fileresource import File
  >>> file = File(os.path.join(filesdir, 'test.txt'), 'test.txt')
  >>> request = TestRequest()
  >>> res = resource.FileResource(file, request)
  >>> res.__name__ = 'ajax.js'
  >>> res
  <FileResource '.../z3c/versionedresource/tests/testfiles/test.txt'>
  >>> res.cacheTimeout
  315360000
  >>> res()
  'http://127.0.0.1/@@/1.0.0/ajax.js'

Two factories, one for files and one for images is used:

  >>> factory = resource.FileResourceFactory(
  ...     os.path.join(filesdir, 'test.txt'), None, 'test.txt')
  >>> factory
  <z3c.versionedresource.resource.FileResourceFactory object at ...>
  >>> factory(request)
  <FileResource '.../z3c/versionedresource/tests/testfiles/test.txt'>

  >>> factory = resource.ImageResourceFactory(
  ...     os.path.join(filesdir, 'test.gif'), None, 'test.gif')
  >>> factory
  <z3c.versionedresource.resource.ImageResourceFactory object at ...>
  >>> factory(request)
  <FileResource '.../z3c/versionedresource/tests/testfiles/test.gif'>


Directory Resource
~~~~~~~~~~~~~~~~~~

Let's now turn to directories. The trick here is that we need to set all the
factories correctly. So let's create the resource first:

  >>> from zope.app.publisher.browser.directoryresource import Directory

  >>> request = TestRequest()
  >>> res = resource.DirectoryResource(
  ...     Directory(os.path.join(filesdir, 'subdir'), None, 'subdir'), request)
  >>> res.__name__ = 'subdir'
  >>> res
  <DirectoryResource '.../z3c/versionedresource/tests/testfiles/subdir'>
  >>> res()
  'http://127.0.0.1/@@/1.0.0/subdir'

Let's try to traverse to some files in the directory:

  >>> res.publishTraverse(request, 'test.gif')
  <FileResource '.../z3c/versionedresource/tests/testfiles/subdir/test.gif'>

We also have a factory for it:

  >>> factory = resource.DirectoryResourceFactory(
  ...     os.path.join(filesdir, 'subdir'), None, 'subdir')
  >>> factory
  <z3c.versionedresource.resource.DirectoryResourceFactory object at ...>
  >>> factory(request)
  <DirectoryResource '.../z3c/versionedresource/tests/testfiles/subdir'>


Custom ZCML Directives
----------------------

To make the new resources easily usable, we also need custom resource
directives:

  >>> from zope.configuration import xmlconfig
  >>> import z3c.versionedresource
  >>> context = xmlconfig.file('meta.zcml', z3c.versionedresource)

Let's register simple versioned resource:

  >>> context = xmlconfig.string("""
  ... <configure
  ...     xmlns:browser="http://namespaces.zope.org/browser">
  ...   <browser:versionedResource
  ...       name="zcml-test.gif"
  ...       image="%s"
  ...       />
  ... </configure>
  ... """ %os.path.join(filesdir, 'test.gif') , context=context)

Now we can access the resource:

  >>> resources.publishTraverse(request, '1.0.0')\
  ...          .publishTraverse(request, 'zcml-test.gif')()
  'http://127.0.0.1/@@/1.0.0/zcml-test.gif'

You can also specify a simple file resource,

  >>> context = xmlconfig.string("""
  ... <configure
  ...     xmlns:browser="http://namespaces.zope.org/browser">
  ...   <browser:versionedResource
  ...       name="zcml-test.txt"
  ...       file="%s"
  ...       />
  ... </configure>
  ... """ %os.path.join(filesdir, 'test.txt') , context=context)

  >>> resources.publishTraverse(request, '1.0.0')\
  ...          .publishTraverse(request, 'zcml-test.txt').context
  <zope.app.publisher.fileresource.File object at ...>

  >>> unregister('zcml-test.txt')

as well as a page template.

  >>> context = xmlconfig.string("""
  ... <configure
  ...     xmlns:browser="http://namespaces.zope.org/browser">
  ...   <browser:versionedResource
  ...       name="zcml-test.html"
  ...       template="%s"
  ...       />
  ... </configure>
  ... """ %os.path.join(filesdir, 'test.pt') , context=context)

  >>> resources.publishTraverse(request, '1.0.0')\
  ...          .publishTraverse(request, 'zcml-test.html').context
  <zope.app.publisher.pagetemplateresource.PageTemplate object at ...>

Note that the page template resource cannot be a versioned resource, since it
has dynamic components:

  >>> resources.publishTraverse(request, '1.0.0')\
  ...          .publishTraverse(request, 'zcml-test.html')()
  u'<h1>Test</h1>\n'

Note: Eeek, `zope.app.publisher.browser` is broken here. We should have
gotten a URL back.

  >>> unregister('zcml-test.html')

Finally, a factory can also be passed in:

  >>> context = xmlconfig.string("""
  ... <configure
  ...     xmlns:browser="http://namespaces.zope.org/browser">
  ...   <browser:versionedResource
  ...       name="zcml-dyn.html"
  ...       factory="z3c.versionedresource.tests.test_doc.ResourceFactory"
  ...       />
  ... </configure>
  ... """, context=context)

  >>> resources.publishTraverse(request, '1.0.0')\
  ...          .publishTraverse(request, 'zcml-dyn.html')
  <ResourceFactory>

  >>> unregister('zcml-dyn.html')

Let's now create a directory resource:

  >>> context = xmlconfig.string("""
  ... <configure
  ...     xmlns:browser="http://namespaces.zope.org/browser">
  ...   <browser:versionedResourceDirectory
  ...       name="zcml-subdir"
  ...       directory="%s"
  ...       />
  ... </configure>
  ... """ %os.path.join(filesdir, 'subdir') , context=context)

And access it:

  >>> resources.publishTraverse(request, '1.0.0')\
  ...          .publishTraverse(request, 'zcml-subdir')()
  'http://127.0.0.1/@@/1.0.0/zcml-subdir'

The directives also have some error handling built-in. So let's have a
look. In the ``browser:versionedResource`` directive, you can only specify
either a template, file, image or factory:

  >>> context = xmlconfig.string("""
  ... <configure
  ...     xmlns:browser="http://namespaces.zope.org/browser">
  ...   <browser:versionedResource
  ...       name="zcml-test.gif"
  ...       file="test.gif"
  ...       image="test.gif"
  ...       />
  ... </configure>
  ... """, context=context)
  Traceback (most recent call last):
  ...
  ZopeXMLConfigurationError: File "<string>", line 4.2-8.8
      ConfigurationError: Must use exactly one of factory or file or
                          image or template attributes for resource directives

The resource directive on the other hand, ensures that the specified path is a
directory:

  >>> context = xmlconfig.string("""
  ... <configure
  ...     xmlns:browser="http://namespaces.zope.org/browser">
  ...   <browser:versionedResourceDirectory
  ...       name="zcml-subdir"
  ...       directory="/foo"
  ...       />
  ... </configure>
  ... """, context=context)
  Traceback (most recent call last):
  ...
  ZopeXMLConfigurationError: File "<string>", line 4.2-7.8
        ConfigurationError: Directory /foo does not exist


Listing All Resources
---------------------

Finally, there exists a script that will list all resources registered as
versioned resources with the system.

  >>> from z3c.versionedresource import list

  >>> list.produceResources(list.get_options(
  ...   ['-u', 'http://zope.org',
  ...    '-l', 'z3c.versionedresource.tests.test_doc.ITestLayer',
  ...    '--list-only',
  ...    os.path.join(os.path.dirname(list.__file__), 'tests', 'simple.zcml')]
  ...   ))
  http://zope.org/@@/1.0.0/zcml-subdir/test.gif
  http://zope.org/@@/1.0.0/zcml-subdir/subsubdir/subtest.gif
  http://zope.org/@@/1.0.0/zcml-test.gif

You can also produce the resources in a directory:

  >>> import tempfile
  >>> outdir = tempfile.mkdtemp()

  >>> list.produceResources(list.get_options(
  ...   ['-u', 'http://zope.org',
  ...    '-l', 'z3c.versionedresource.tests.test_doc.ITestLayer',
  ...    '-d', outdir,
  ...    os.path.join(os.path.dirname(list.__file__), 'tests', 'simple.zcml')]
  ...   ))
  /.../1.0.0

  >>> ls(outdir)
  d 1.0.0             4096
  >>> ls(os.path.join(outdir, '1.0.0'))
  d zcml-subdir       4096
  f zcml-test.gif     909
  >>> ls(os.path.join(outdir, '1.0.0', 'zcml-subdir'))
  d subsubdir         4096
  f test.gif          909
  >>> ls(os.path.join(outdir, '1.0.0', 'zcml-subdir', 'subsubdir'))
  f subtest.gif       909

The module consists of several small helper functions, so let's look at them
to verify their correct behavior.


`getResources(layerPath, url='http://localhost/')` Function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This function retrieves all versioned resources from the system for a given
layer. Optionally a URL can be passed in to alter the resource URLs.

  >>> resources = list.getResources(
  ...     ['z3c.versionedresource.tests.test_doc.ITestLayer',
  ...      'z3c.versionedresource.tests.test_doc.ITestLayer2'])
  >>> sorted(resources)
  [(u'zcml-subdir', <DirectoryResource u'.../testfiles/subdir'>),
   (u'zcml-test.gif', <FileResource u'.../testfiles/test.gif'>)]

As you can see, this list only provides the first layer. It is the
responsibility of the consuming code to digg deeper into the directory
resources.


`getResourceUrls(resources)` Function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once we have the list of resources, we can produce a full list of all
available paths.

  >>> sorted(list.getResourceUrls(resources))
  [u'http://localhost/@@/1.0.0/zcml-subdir/subsubdir/subtest.gif',
   u'http://localhost/@@/1.0.0/zcml-subdir/test.gif',
   u'http://localhost/@@/1.0.0/zcml-test.gif']


`storeResource(dir, name, resource, zip=False)` Function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The more interesting use case, however, is this function, which stores the
resources in a directory. First we need to create an output directory:

  >>> outdir = tempfile.mkdtemp()

We can now store a resource to it:

  >>> list.storeResource(outdir, resources[1][0], resources[1][1])
  >>> ls(outdir)
  f zcml-test.gif     909

Let's now zip it:

  >>> list.storeResource(outdir, resources[1][0], resources[1][1], True)
  >>> ls(outdir)
  f zcml-test.gif     252

When storing a directory resource, all sub-items are stored as well:

  >>> list.storeResource(outdir, resources[0][0], resources[0][1], True)
  >>> ls(outdir)
  d zcml-subdir       4096
  f zcml-test.gif     252

  >>> ls(os.path.join(outdir, 'zcml-subdir'))
  d subsubdir 4096
  f test.gif  259

  >>> ls(os.path.join(outdir, 'zcml-subdir', 'subsubdir'))
  f subtest.gif       272


Some odds and ends
~~~~~~~~~~~~~~~~~~

Let's use the `main()` function too. It is the one used by the script, but
always raises a system exist:

  >>> list.main()
  Traceback (most recent call last):
  ...
  SystemExit: 2

  >>> list.main(['foo'])
  Traceback (most recent call last):
  ...
  SystemExit: 1

  >>> list.main(
  ...   ['-l', 'z3c.versionedresource.tests.test_doc.ITestLayer',
  ...    '--list-only',
  ...    os.path.join(os.path.dirname(list.__file__), 'tests', 'simple.zcml')]
  ...   )
  Traceback (most recent call last):
  ...
  SystemExit: 0

If the positional argument is missing, then we get a parser error:

  >>> list.main(
  ...   ['-l', 'z3c.versionedresource.tests.test_doc.ITestLayer',
  ...    '--list-only'])
  Traceback (most recent call last):
  ...
  SystemExit: 2
