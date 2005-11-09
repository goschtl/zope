====================================
Package-relative resource references
====================================

The `zope.configuration.path` module provides a way to refer to and
open a file using a package-relative path.  This is especially useful
for packages imported from ZIP files (including eggs).  Such files are
considered resources, and may only be opened in read-only mode.

Resource references have a dual personality:  They are both strings
and objects with interesting non-string methods.  The string behavior
is intended to help support compatibility for code that was written
before this API existed, while new code can use the extended API for
more flexibility.

There are two interesting functions: `new()` is used to construct a
new path reference, and `open()` is used to open the resource as a
file-like object.

`new()` takes three arguments: a path, a package, and a base path.
Only the first is required; passing `None` for the `package` and
`basepath` arguments is equivalent to omitting them.

The idea of the resource references is that they can carry along
additional information that allows them to retain package-relative
information, so they are most interesting when the `package` argument
to the constructor is non-`None`.  Let's take a look at what this
provides::

  >>> import os
  >>> import zope.resource

  >>> ref = zope.resource.new("README.txt", package=zope.resource)

If we examine the reference as a string, we get a path that points
into the package::

  >>> directory = os.path.dirname(zope.resource.__file__)
  >>> ref == os.path.join(directory, "README.txt")
  True

The resource can be opened using the `open()` function (which
also accepts simple strings)::

  >>> f = zope.resource.open(ref)
  >>> f.readline()
  '====================================\n'
  >>> f.close()

While this looks little different from using a simple string to refer
to the resource file, it provides more functionality if the resource
being referenced is part of a package contained in a ZIP archive.
Let's add a convenient ZIP file containing a Python package to the
module search path::

  >>> import sys

  >>> here = os.path.normpath(os.path.dirname(__file__))
  >>> zipfile = os.path.join(here, "zippitysample.zip")
  >>> sys.path.append(zipfile)

We can now import the package contained in the zipfile and load
resources from it::

  >>> import zippity.sample
  >>> ref = zope.resource.new("configure.zcml", package=zippity.sample)

  >>> f = zope.resource.open(ref)
  >>> f.readline()
  '<configure\n'
  >>> f.close()

Note that only read modes are supported::

  >>> zope.resource.open(ref, "w")
  Traceback (most recent call last):
    ...
  ValueError: `mode` must be a read-only mode

  >>> zope.resource.open(ref, "w+")
  Traceback (most recent call last):
    ...
  ValueError: `mode` must be a read-only mode

  >>> zope.resource.open(ref, "a")
  Traceback (most recent call last):
    ...
  ValueError: `mode` must be a read-only mode

  >>> zope.resource.open(ref, "a+")
  Traceback (most recent call last):
    ...
  ValueError: `mode` must be a read-only mode
