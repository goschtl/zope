##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Support for handling package configuration files."""

import glob
import os
import posixpath
import re
import urllib

from distutils.core import Extension
from StringIO import StringIO

from zpkgtools import cfgparser


PACKAGE_CONF = "package.conf"

# SCHEMA is defined at the end of the module to allow referenced
# functions to be defined first.


def loadPackageInfo(pkgname, directory, reldir, file=None):
    print (pkgname, directory, reldir, file)
    if not file:
        file = PACKAGE_CONF
    path = os.path.join(directory, file)
    if os.path.exists(path):
        path = os.path.realpath(path)
        url = "file://" + urllib.pathname2url(path)
        f = open(path)
    else:
        # Initialize using the cfgparser so we still get a package
        # data object with the right attributes:
        url = "<no file>"
        f = StringIO("")
    try:
        p = cfgparser.Parser(f, url, SCHEMA)
        pkginfo = p.load()
    finally:
        f.close()
    pkginfo.extensions = [create_extension(ext, pkgname, directory, reldir)
                          for ext in pkginfo.extension]
    if reldir:
        pkginfo.documentation = expand_globs(directory, reldir,
                                             pkginfo.documentation)
        pkginfo.script = expand_globs(directory, reldir, pkginfo.script)
    return pkginfo


def expand_globs(directory, reldir, globlist):
    results = []
    pwd = os.getcwd()
    os.chdir(directory)
    try:
        for g in globlist:
            gs = g.replace("/", os.sep)
            filenames = glob.glob(gs)
            if not filenames:
                raise ValueError("filename pattern %r doesn't match any files" % g)
            results += [posixpath.join(reldir, fn.replace(os.sep, "/"))
                        for fn in filenames]
    finally:
        os.chdir(pwd)
    return results


def cpp_definition(s):
    r"""Return a 2-tuple representing a CPP #define.

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
    section.name = section.getSectionName()
    if not section.name:
        raise ValueError("extensions must be named")
    if not section.source:
        raise ValueError("at least one extension source file must be listed")
    if len(section.language) > 1:
        raise ValueError("language can only be specified once")
    return section


def create_extension(section, pkgname, directory, reldir):
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
    return Extension(**kwargs)


def path_ref(s):
    """Datatype for a local path reference.

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


SCHEMA = cfgparser.Schema(
    ({"script": path_ref, "documentation": path_ref}, ["extension"], None),
    {"extension": ({"source": path_ref, "depends-on": path_ref,
                    "define" : cpp_definition, "undefine": cpp_names,
                    "language": str,
                    },
                   (), extension),
     })
