"""Path reference to package-relative resources.
"""
__docformat__ = "reStructuredText"

import errno
import os
import StringIO

import zope.interface

try:
    import pkg_resources
except ImportError:
    pkg_resources = None


class IResourceReference(zope.interface.Interface):

    def open(mode="rb"):
        """Open the referenced resource, returning a file-like object.

        Only 'read' modes are supported.

        """


def newReference(path, package=None, basepath=None):

    if os.path.isabs(path):
        return PathReference(path)

    # Got a relative path, combine with base path.
    # If we have no basepath, compute the base path from the package
    # path.

    if not basepath:
        if package is None:
            basepath = os.getcwd()
        else:
            basepath = os.path.dirname(package.__file__)

    p = os.path.join(basepath, path)
    p = os.path.normpath(p)
    p = os.path.abspath(p)

    if package:
        return PackagePathReference(p, package, path)
    else:
        return PathReference(p)


class PathReference(str):

    zope.interface.implements(IResourceReference)

    def __add__(self, other):
        path = str(self) + other
        return self.__class__(path)

    def open(self, mode="rb"):
        return open(self, mode)


class PackagePathReference(str):

    zope.interface.implements(IResourceReference)

    def __new__(cls, value, package, relpath):
        assert package
        self = str.__new__(cls, value)
        self._package = package
        self._relpath = relpath
        return self

    def __add__(self, other):
        value = str(self) + other
        relpath = self._relpath + other
        return self.__class__(value, self._package, relpath)

    def open_pkg_resources(self, mode="rb"):
        try:
            data = pkg_resources.resource_string(
                self._package.__name__, self._relpath)
        except IOError, e:
            if len(e.args) == 1:
                # zipimport raises IOError w/ insufficient arguments
                raise IOError(errno.ENOENT, "file not found", self)
            else:
                raise
        f = StringIO.StringIO(data)
        f.name = self
        f.mode = mode
        return f

    def open_path_or_loader(self, mode="rb"):
        try:
            loader = self._package.__loader__
        except AttributeError:
            for dir in self._package.__path__:
                filename = os.path.join(dir, self._relpath)
                if os.path.exists(filename):
                    break
            return open(filename, mode)
        else:
            dir = os.path.dirname(self._package.__file__)
            filename = os.path.join(dir, self._relpath)
            return loader.get_data(self._package.__name__)

    if pkg_resources:
        open = open_pkg_resources
    else:
        open = open_path_or_loader


def openResource(path, mode="rb"):
    if not mode.startswith("r"):
        raise ValueError("`mode` must be a read-only mode")
    if IResourceReference.providedBy(path):
        return path.open(mode)
    else:
        return open(path, mode)
