====================================
Package-relative resource references
====================================

The `zope.filereference` package provides a way to refer to and open a
file using a package-relative path.  This is especially useful for
packages imported from ZIP files (including eggs).  Such files may
only be opened in read-only mode.

File references have a dual personality:  They are both strings
and objects with interesting non-string methods.  The string behavior
is intended to help support compatibility for code that was written
before this API existed, while new code can use the extended API for
more flexibility.

There are several interesting functions: `new()` is used to construct
a new path reference, and `open()` is used to open the resource as a
file-like object.  Additional functions correlate to the common
functions `os.path.exists()`, `os.path.isdir()`, and
`os.path.isfile()`.

`new()` takes three arguments: a path, a package, and a base path.
Only the first is required; passing `None` for the `package` and
`basepath` arguments is equivalent to omitting them.

The idea of the resource references is that they can carry along
additional information that allows them to retain package-relative
information, so they are most interesting when the `package` argument
to the constructor is non-`None`.  Let's take a look at what this
provides::

  >>> import os
  >>> import zope.filereference

  >>> ref = zope.filereference.new("README.txt", package=zope.filereference)

When a file reference is passed to `new()`, it is returned instead of
generating a new reference::

  >>> ref2 = zope.filereference.new(ref)
  >>> ref2 is ref
  True

If we examine the reference as a string, we get a path that points
into the package::

  >>> directory = os.path.dirname(zope.filereference.__file__)
  >>> filename = os.path.join(directory, "README.txt")
  >>> ref == filename
  True

The `getmtime()` function can be used to get the modification time for
a referenced file if it's available::

  >>> zope.filereference.getmtime(ref) == os.path.getmtime(filename)
  True

The reference can be opened using the `open()` function (which
also accepts simple strings)::

  >>> f = zope.filereference.open(ref)
  >>> f.readline()
  '====================================\n'
  >>> f.close()

We can also ask whether the reference points to a file that exists::

  >>> zope.filereference.exists(ref)
  True
  >>> zope.filereference.isfile(ref)
  True
  >>> zope.filereference.isdir(ref)
  False

While this looks little different from using a simple string to refer
to the referenced file, it provides more functionality if the file
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
  >>> ref = zope.filereference.new("configure.zcml", package=zippity.sample)

  >>> f = zope.filereference.open(ref)
  >>> f.readline()
  '<configure\n'
  >>> f.close()

The query methods provide the expected results as well::

  >>> zope.filereference.exists(ref)
  True
  >>> zope.filereference.isdir(ref)
  False
  >>> zope.filereference.isfile(ref)
  True

Note that only read modes are supported::

  >>> zope.filereference.open(ref, "w")
  Traceback (most recent call last):
    ...
  ValueError: `mode` must be a read-only mode

  >>> zope.filereference.open(ref, "w+")
  Traceback (most recent call last):
    ...
  ValueError: `mode` must be a read-only mode

  >>> zope.filereference.open(ref, "a")
  Traceback (most recent call last):
    ...
  ValueError: `mode` must be a read-only mode

  >>> zope.filereference.open(ref, "a+")
  Traceback (most recent call last):
    ...
  ValueError: `mode` must be a read-only mode

References to directories in ZIP files work as well::

  >>> ref = zope.filereference.new("sample", package=zippity)
  >>> zope.filereference.exists(ref)
  True
  >>> zope.filereference.isdir(ref)
  True
  >>> zope.filereference.isfile(ref)
  False
  
If we refer to a resource in a ZIP archive that doesn't exist, we get
the expected results::

  >>> ref = zope.filereference.new("MISSING.txt", package=zippity.sample)

  >>> zope.filereference.exists(ref)
  False
  >>> zope.filereference.isfile(ref)
  False
  >>> zope.filereference.isdir(ref)
  False

Getting a local package-relative reference
------------------------------------------

It's easy to create package-relative references from within a
package, or to files in other packages.  Let's start by specifying the
package we're interested in.  We'll need a candidate package and the
file name we're expecting to see::

  >>> import xml.sax
  >>> initfile = os.path.join(os.path.dirname(xml.sax.__file__), "__init__.py")

Let's start by specifying the package using the package module::

  >>> ref = zope.filereference.packageReference(
  ...     "__init__.py", package=xml.sax)

  >>> ref == initfile
  True

This will also work when we specify the context package using a
string::

  >>> ref = zope.filereference.packageReference(
  ...     "__init__.py", package="xml.sax")

  >>> ref == initfile
  True

To demonstrate this function from the context of a real package, we're
going to use the `testmodule` module in this package.  We'll import
the reference created there and check that it produces the reference
we expect::

  >>> initfile = os.path.join(
  ...     os.path.dirname(zope.filereference.__file__), "__init__.py")

  >>> from zope.filereference.testmodule import ref
  >>> ref == initfile
  True
