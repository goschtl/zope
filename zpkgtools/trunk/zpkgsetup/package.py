##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Support for handling package configuration files.

The package configuration files handled by this module provide
information about the software and documentation contents of a
distribution component.  The same kinds of information can be
described for any component, with the exception that extensions only
make sense for package components.

Package configuration files use a syntax very like the `ZConfig`_
package, but fewer features are available.  The specific syntax is
implemented by the `zpkgsetup.cfgparser` module.

.. _ZConfig:  http://www.zope.org/Members/fdrake/zconfig/

There are only a few types of information which can appear in a
package configuration file; the file is intended to describe what a
package provides that is not a module or data file.  The three types
of things which can be listed in the file are:

- scripts
- documentation
- extensions

The scripts and documentation files are listed very simply::

  documentation  *.txt
  documentation  apiref.pdf

  script  scritps/*

The value to the right of the identifying keyword is a portable glob
pattern, where *portable* here means the pattern uses the POSIX
notation.  Path components should be separated by forward slashes
(like all paths used with `distutils`), ``?`` can be replaced by any
single character, and ``*`` can be replaced by zero or more
characters.


:Variables:
  - `PACKAGE_CONF`:  Name of the package information file.

:Groups:
  - `Public interface`: loadCollectionInfo loadPackageInfo
  - `Helper functions`: create_extension expand_globs read_package_info
  - `Datatype functions`: cpp_definition cpp_names path_ref extension

"""

import glob
import os
import posixpath
import re
import urllib

from StringIO import StringIO

from zpkgsetup import cfgparser
from zpkgsetup import dist
from zpkgsetup import urlutils


PACKAGE_CONF = "SETUP.cfg"


def loadPackageInfo(pkgname, directory, reldir):
    """Load package information for a Python package.

    :return: Package information object.

    :Parameters:
      - `pkgname`: Full name of the Python package to which the
        information being read applies.  This is needed to construct
        Extension objects properly.
      - `directory`: Directory containing the package's __init__.py file.
      - `reldir`: Relative directory path with which file names from
        the information file will be joined.  This should be in POSIX
        notation.  It will not be used to locate files.

    """
    pkginfo = read_package_info(directory, reldir)
    pkginfo.extensions = [create_extension(ext, pkgname, reldir)
                          for ext in pkginfo.extension]
    return pkginfo


def loadCollectionInfo(directory, reldir):
    """Load package information for a collection.

    :return: Package information object.

    :Parameters:
      - `directory`: Directory containing the collection's files.
      - `reldir`: Relative directory path with which file names from
        the information file will be joined.  This should be in POSIX
        notation.  It will not be used to locate files.

    """
    pkginfo = read_package_info(directory, reldir)
    if pkginfo.extension:
        raise ValueError("extensions cannot be defined in collections")
    pkginfo.extensions = []
    return pkginfo


def read_package_info(directory, reldir=None):
    """Read the package information file from a specified directory.

    :return: Package information object.

    :Parameters:
      - `directory`: Directory containing the collection's files.
      - `reldir`: Relative directory path with which file names from
        the information file will be joined.  This should be in POSIX
        notation.  It will not be used to locate files.  It may be
        omitted or None; if so, filenames are not 'relocated' relative
        to where they are found.

    """
    path = os.path.join(directory, PACKAGE_CONF)
    if os.path.exists(path):
        path = os.path.realpath(path)
        url = urlutils.file_url(urllib.pathname2url(path))
        f = open(path)
    else:
        # Initialize using the cfgparser so we still get a package
        # data object with the right attributes:
        url = "<no file>"
        f = StringIO("")
    try:
        p = cfgparser.Parser(f, url, PackageSchema(directory, reldir))
        pkginfo = p.load()
    finally:
        f.close()
    pkginfo.documentation = expand_globs(directory, reldir,
                                         pkginfo.documentation)
    pkginfo.header = expand_globs(directory, reldir, pkginfo.header)
    pkginfo.script = expand_globs(directory, reldir, pkginfo.script)

    # need to post-process the data_files so included directories are
    # handled properly; distutils expects everything to be a file!
    #
    # XXX need tests!
    #
    datamap = {}
    for dir, paths in pkginfo.data_files:
        expand_data(directory, reldir, dir, paths, datamap)
    if "." in datamap and datamap["."] == []:
        del datamap["."]
    pkginfo.data_files = datamap.items()

    return pkginfo


def expand_data(directory, reldir, targetdir, paths, datamap):
    #
    # `directory` is where we find things
    #
    # `reldir` is the relative location of directory in the source; we
    # need it so we can rip it off of the values in `paths`
    #
    # `targetdir` is where we want the things in `paths` copied in
    # POSIX notation
    #
    # `paths` is a list of paths to things we want copied, in POSIX
    # notation, with `reldir` prepended
    #
    # `datamap` is a mapping from target directory -> [files], where
    # files are really paths to actual files (not directories!) that
    # are to be copied to the target directory; the file paths are
    # given in POSIX notation and are prefixed by `reldir`
    #
    # All directories must be represented in the data map, even if
    # they're empty.
    #
    targetdir = posixpath.normpath(targetdir)

    # Make sure there's an entry for every directory we look at; that
    # ensures distutils will create empty directories for us.
    L = datamap.setdefault(targetdir, [])

    if reldir:
        prefix = posixpath.join(reldir, "")
    else:
        prefix = ""

    # for files, add to the list, otherwise recursively scan
    for src in paths:
        # strip `reldir`, convert to local path notation
        localpath = src[len(prefix):].replace("/", os.sep)
        # find the referenced path
        fullpath = os.path.join(directory, localpath)
        if os.path.isfile(fullpath):
            L.append(src)
        else:
            # directory; recurse
            basename = os.path.basename(fullpath)
            expand_data(
                directory, reldir, posixpath.join(targetdir, basename),
                [posixpath.join(src, name) for name in os.listdir(fullpath)],
                datamap)


def create_extension(section, pkgname, reldir):
    """Create an extension object from a configuration section.

    :Parameters:
      - `section`: Section object from the configuration file.
      - `pkgname`: Full name of the containing package.  This should
        be an empty string or ``None`` if the extension is not in a
        package.
      - `reldir`: Directory in which the extension lives, relative to
        the top of the distribution, given in POSIX notation.

    :rtype: `zpkgsetup.dist.ZPkgExtension`

    """
    kwargs = {}
    if pkgname:
        kwargs["name"] = "%s.%s" % (pkgname, section.name)
    else:
        kwargs["name"] = section.name
    kwargs["sources"] = [posixpath.join(reldir, fn)
                         for fn in section.source]
    if section.define:
        kwargs["define_macros"] = section.define
    if section.undefine:
        kwargs["undef_macros"] = undefs = []
        for L in section.undefine:
            undefs.extend(L)
    if section.depends_on:
        kwargs["depends"] = [posixpath.join(reldir, fn)
                             for fn in section.depends_on]
    if section.language:
        kwargs["language"] = section.language[0]
    if reldir and reldir != ".":
        kwargs["include_dirs"] = [reldir]
    return dist.ZPkgExtension(**kwargs)


def expand_globs(directory, reldir, globlist):
    """Expand glob patterns for directory.

    :Parameters:
      - `directory`: The path to the directory to which the glob
        patterns are relative to.
      - `reldir`: Base directory to use for returning glob expansions.
        This should be a relative path in POSIX notation.  This is not
        used for locating files.
      - `globlist`: List of glob patterns in POSIX notation.  The
        patterns may refer to child directories of `directory`.

    :return: List of expansions in POSIX notation, using `reldir` as
      the base directory.

    Note that `directory` and `reldir` are two different names for the
    same directory.

    :warning: This function is not thread safe, as it changes the
      current working directory while it is running.

    """
    results = []
    pwd = os.getcwd()
    os.chdir(directory)
    try:
        for g in globlist:
            gs = g.replace("/", os.sep)
            filenames = glob.glob(gs)
            if not filenames:
                raise ValueError(
                    "filename pattern %r doesn't match any files" % g)
            filenames = [fn.replace(os.sep, "/") for fn in filenames]
            if reldir:
                filenames = [posixpath.join(reldir, fn) for fn in filenames]
            results += filenames
    finally:
        os.chdir(pwd)
    return results


# datatype functions referenced by the schema:

def cpp_definition(s):
    r"""Return a 2-tuple representing a CPP #define.

    :rtype: (str, str or None)

    The first element of the tuple is the name to define, and the
    second is the value to use as the replacement text.  In the input,
    the two parts should be separated by an equal sign.

    >>> cpp_definition('NAME=VALUE')
    ('NAME', 'VALUE')
    >>> cpp_definition('NAME=')
    ('NAME', '')

    Whitespace around the equal sign are ignored:

    >>> cpp_definition('NAME   =\tVALUE')
    ('NAME', 'VALUE')

    If there is no equal sign, and defininition with no replacement
    text is used (equivalent to '#define NAME'):

    >>> cpp_definition('NAME')
    ('NAME', None)

    ValueError is raised if there is an error in the input:

    >>> cpp_definition('not-a-cpp-symbol')
    Traceback (most recent call last):
      ...
    ValueError: not a valid C identifier: 'not-a-cpp-symbol'

    """
    if "=" in s:
        name, value = s.split("=", 1)
        name = name.rstrip()
        value = value.lstrip()
    else:
        name = s
        value = None
    if _cpp_ident_match(name) is None:
        raise ValueError("not a valid C identifier: %r" % name)
    return name, value


def cpp_names(s):
    r"""Return a list of CPP symbols from a string.

    :rtype: [str, ...]

    >>> cpp_names('NAME')
    ['NAME']
    >>> cpp_names('NAME1 NAME_2 A_B_C A123')
    ['NAME1', 'NAME_2', 'A_B_C', 'A123']

    If something is included which is not a valid identifier for CPP,
    ValueError is raised:

    >>> cpp_names('not-really!')
    Traceback (most recent call last):
      ...
    ValueError: not a valid C identifier: 'not-really!'

    >>> cpp_names('NAME ANOTHER not-really!')
    Traceback (most recent call last):
      ...
    ValueError: not a valid C identifier: 'not-really!'

    """
    names = s.split()
    for name in names:
        if _cpp_ident_match(name) is None:
            raise ValueError("not a valid C identifier: %r" % name)
    return names

_cpp_ident_match = re.compile("[A-Za-z_][A-Za-z_0-9]*$").match


def extension(section):
    """Transform `section`, checking several fields for valid values.

    :param section: Configuration section.
    :return: Modified section.
    """
    section.name = section.getSectionName()
    if not section.name:
        raise ValueError("extensions must be named")
    if not section.source:
        raise ValueError("at least one extension source file must be listed")
    if len(section.language) > 1:
        raise ValueError("language can only be specified once")
    return section


def path_ref(s):
    """Datatype for a local path reference.

    :rtype: str

    >>> path_ref('README.txt')
    'README.txt'
    >>> path_ref('./README.txt')
    'README.txt'
    >>> path_ref('foo/bar/file.txt')
    'foo/bar/file.txt'

    If a reference is not a relative path, ValueError is raised:

    >>> path_ref('/absolute/path')
    Traceback (most recent call last):
      ...
    ValueError: absolute paths are not allowed: '/absolute/path'

    >>> path_ref('/')
    Traceback (most recent call last):
      ...
    ValueError: absolute paths are not allowed: '/'

    References which contain Windows drive letters are not allowed:

    >>> path_ref('c:README.txt')
    Traceback (most recent call last):
      ...
    ValueError: Windows drive letters are not allowed: 'c:README.txt'

    If a reference is relative but points outside the local directory
    hierarchy, ValueError is raised:

    >>> path_ref('../somefile')
    Traceback (most recent call last):
      ...
    ValueError: relative paths may not point outside the containing tree: '../somefile'

    """
    if not s:
        raise ValueError("path references may not be empty")
    if s.find(":") == 1:
        # looks like a windows drive letter:
        raise ValueError("Windows drive letters are not allowed: %r" % s)
    p = posixpath.normpath(s)
    if p[:1] == "/":
        raise ValueError("absolute paths are not allowed: %r" % s)
    parts = p.split("/")
    if parts[0] == "..":
        raise ValueError("relative paths may not point outside"
                         " the containing tree: %r" % s)
    return p


class PackageSchema(cfgparser.Schema):
    """Schema implementation with a <data-files> section type.

    The <data-files> sections have keys that are glob-expanded (based
    on information passed to the constructor) and combined into a
    single ``data_files`` member on the resulting package information
    object.  The value of the ``data_files`` attribute is suitable for
    passing to the `distutils.core.setup()` function.

    """

    def __init__(self, directory, reldir):
        cfgparser.Schema.__init__(
            self,
            ({"script": path_ref,
              "documentation": path_ref,
              "header": path_ref},
             ["extension"], None),
            {"extension": ({"source": path_ref, "depends-on": path_ref,
                            "define" : cpp_definition, "undefine": cpp_names,
                            "language": str,
                            },
                           (), extension),
             }
            )
        self.__cf = None
        self.__datafiles = None
        self.__directory = directory
        self.__reldir = reldir

    def getConfiguration(self):
        assert self.__cf is None
        self.__cf = cfgparser.Schema.getConfiguration(self)
        self.__cf.data_files = []
        return self.__cf

    def startSection(self, parent, typename, name):
        if self.__datafiles is not None:
            raise cfgparser.ConfigurationError(
                "can't nest another section inside <data-files> section")
        if typename == "data-files":
            if not name:
                raise cfgparser.ConfigurationError(
                    "<data-files> section must have a name")
            normname = posixpath.normpath(name)
            for target, files in self.__cf.data_files:
                if target == normname:
                    raise cfgparser.ConfigurationError(
                        "can't have two sections of the same name:"
                        " <data-files %s>" % name)
            self.__datafiles = []
            self.__cf.data_files.append((normname, self.__datafiles))
            # The return value is passed around, but that's it
            return ()
        else:
            return cfgparser.Schema.startSection(self, parent, typename, name)

    def endSection(self, parent, typename, name, child):
        if self.__datafiles is None:
            cfgparser.Schema.endSection(self, parent, typename, name, child)
        else:
            # mutate self.__datafiles since the reference from
            # self.__cf.data_files is what's actually used
            self.__datafiles[:] = expand_globs(self.__directory,
                                               self.__reldir,
                                               self.__datafiles)
            self.__datafiles = None

    def addValue(self, section, key, value):
        if self.__datafiles is not None:
            if value:
                raise cfgparser.ConfigurationError(
                    "each entry in a <data-files> section must be"
                    " a single glob pattern")
            self.__datafiles.append(key)
        else:
            cfgparser.Schema.addValue(self, section, key, value)
