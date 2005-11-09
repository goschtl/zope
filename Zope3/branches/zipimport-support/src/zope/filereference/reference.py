##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""References to package-relative resources.

"""
__docformat__ = "reStructuredText"

import __builtin__
import errno
import os
import StringIO

import zope.interface

from zope.filereference.interfaces import IResourceReference

try:
    import pkg_resources
except ImportError:
    pkg_resources = None


def open(path, mode="rb"):
    if not mode.startswith("r"):
        raise ValueError("`mode` must be a read-only mode")
    if IResourceReference.providedBy(path):
        return path.open(mode)
    else:
        return __builtin__.open(path, mode)


def new(path, package=None, basepath=None):

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
        return __builtin__.open(self, mode)


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
        return self._open_packaged_resource(
            mode,
            pkg_resources.resource_string,
            self._package.__name__,
            self._relpath)

    def open_path_or_loader(self, mode="rb"):
        try:
            loader = self._package.__loader__
        except AttributeError:
            for dir in self._package.__path__:
                filename = os.path.join(dir, self._relpath)
                if os.path.exists(filename):
                    break
            return __builtin__.open(filename, mode)
        else:
            dir = os.path.dirname(self._package.__file__)
            filename = os.path.join(dir, self._relpath)
            return self._open_packaged_resource(
                mode, loader.get_data, filename)

    def open(self, mode="rb"):
        #
        # This separate wrapper method is used so that this can always
        # be tested for the case when pkg_resources is not available.
        # See tests.py for how the pkg_resources global is
        # manipulated.
        #
        if pkg_resources:
            return self.open_pkg_resources(mode)
        else:
            return self.open_path_or_loader(mode)

    def _open_packaged_resource(self, mode, opener, *args):
        try:
            data = opener(*args)
        except IOError, e:
            if len(e.args) == 1:
                raise IOError(errno.ENOENT, "file not found", self)
            else:
                raise
        f = StringIO.StringIO(data)
        f.name = self
        f.mode = mode
        return f
