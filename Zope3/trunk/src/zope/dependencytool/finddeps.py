#! /usr/bin/env python2.3
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
"""Script to determine the dependencies of a package or module

This script walks through the modules of a package or only observes a
file-based module to determine its dependencies.

Usage: finddeps.py [options]
Options:
    -a / --all
        Find all dependencies. This means that the program will also scan the
        dependencies originally found in the module.

    -h / --help
        Print this message and exit.

    -l / --long
        If long is specified, the file and line where the dependency occurs is
        reported.

    -d / --dir
        Specify the path of the module that is to be inspected.

    -m / --module
        Specify the dotted name of the module that is to be inspected.

    -z / --zcml
        Also look through ZCML files for dependencies.

Important: Make sure that the PYTHONPATH is set to or includes 'ZOPE3/src'.

$Id$
"""
import sys
import getopt
import os
import re

import zope

from zope.dependencytool.dependency import Dependency
from zope.dependencytool.importfinder import ImportFinder


# Get the Zope base path
ZOPESRC = os.path.dirname(os.path.dirname(zope.__file__))
ZOPESRCPREFIX = os.path.join(ZOPESRC, "")

# Matching expression for python files.
pythonfile = re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*\.py$')
zcmlfile = re.compile(r'[a-zA-Z][a-zA-Z0-9_]*\.zcml$')

# Matching expressions of dotted paths in XML
dottedName = re.compile(r'"[a-zA-Z\.][a-zA-Z0-9_\.]*"')


def stripZopePrefix(path):
    """Remove the '.../src/' prefix from path, if present."""
    if path.startswith(ZOPESRCPREFIX):
        return path[len(ZOPESRCPREFIX):]
    else:
        return path


def usage(code, msg=''):
    """Display help."""
    print >> sys.stderr, '\n'.join(__doc__.split('\n')[:-2])
    if msg:
        print >> sys.stderr, '** Error: ' + str(msg) + ' **'
    sys.exit(code)


def makeDottedName(path):
    """Convert a path to a dotted module name, using sys.path."""
    syspaths = sys.path[1:]
    syspaths.append(os.getcwd())
    for syspath in syspaths:
        syspath = os.path.join(syspath, '')
        if path.startswith(syspath):
            return path[len(syspath):].replace(os.sep, ".")

    raise ValueError, 'Cannot create dotted name.'


def getDependenciesOfPythonFile(path):
    finder = ImportFinder()
    finder.find_imports(open(path, 'rU'), path)
    return finder.get_imports()


def getDependenciesOfZCMLFile(path):
    """Get dependencies from ZCML file."""
    localModule = stripZopePrefix(os.path.dirname(path))
    localModule = localModule.replace(os.sep, '.')
    deps = []
    lineno = 0
    for line in open(path, 'r'):
        lineno += 1
        match = dottedName.findall(line)
        if match:
            match[0] = match[0][1:-1]
            match.append('.'.join(match[0].split('.')[:-1]))

            for name in match:
                if name.startswith('.'):
                    name = localModule + name
                try:
                    __import__(name)
                except:
                    continue
                deps.append(Dependency(name, path, lineno))
    return deps


def filterStandardModules(deps):
    """Try to remove modules from the standard Python library.

    Modules are considered part of the standard library if their
    __file__ is located in the tree rooted at the parent of the
    site-packages directory, but not in the sub-tree in site-packages.
    """
    from distutils import sysconfig
    site_packages = sysconfig.get_python_lib()
    standard_lib = os.path.dirname(site_packages)
    site_packages = os.path.join(site_packages, "")
    standard_lib = os.path.join(standard_lib, "")
    filteredDeps = []
    for dep in deps:
        try:
            module = __import__(dep.path)
        except ImportError:
            continue
        # built-ins (like sys) do not have a file associated
        if not hasattr(module, '__file__'):
            continue
        starts = module.__file__.startswith
        if starts(standard_lib) and not starts(site_packages):
            continue
        filteredDeps.append(dep)
    return filteredDeps


def filterLocalModules(deps, path):
    """Filter out local module imports."""
    # File-based modules cannot have relative imports
    if os.path.isfile(path):
        return deps

    # Filter relative imports
    filteredDeps = []
    for dep in deps:
        module = dep.path.split('.')[0]
        modulePath = os.path.join(path, module)
        if not (os.path.exists(modulePath)
                or os.path.exists(modulePath+'.py')):
            filteredDeps.append(dep)
    deps = filteredDeps

    # Filter absolute imports
    dottedName = makeDottedName(path)
    filteredDeps = []
    for dep in deps:
        if not dep.path.startswith(dottedName):
            filteredDeps.append(dep)

    return filteredDeps


def filterMostGeneral(deps):
    """Return only the parent module and no children.

    for example (foo, foo.bar) --> (foo,)
    """
    newdeps = []
    for dep in deps:
        subpackage = False
        for parentdep in deps:
            if parentdep is not dep and dep.isSubPackageOf(parentdep):
                subpackage = True
                break
        if not subpackage:
            newdeps.append(dep)
    return newdeps


def makeUnique(deps):
    """Remove entries that appear multiple times"""
    uniqueDeps = {}
    for dep in deps:
        if not dep.path in uniqueDeps.keys():
            uniqueDeps[dep.path] = dep
        else:
            uniqueDeps[dep.path].addOccurence(*dep.occurences[0])

    return uniqueDeps.values()


def getDependencies(path, zcml=False):
    """Get all dependencies of a package or module.

    If the path is a package, all Python source files are searched inside it.
    """
    if os.path.isdir(path):
        deps = []
        for file in os.listdir(path):
            filePath = os.path.join(path, file)
            if pythonfile.match(file):
                deps += getDependenciesOfPythonFile(filePath)
            elif zcml and zcmlfile.match(file):
                deps += getDependenciesOfZCMLFile(filePath)
            elif os.path.isdir(filePath):
                filenames = os.listdir(filePath)
                if (  'PUBLICATION.cfg' not in filenames
                      and 'SETUP.cfg' not in filenames
                      and 'DEPENDENCIES.cfg' not in filenames
                      and '__init__.py' in filenames):
                    deps += getDependencies(filePath)

    elif os.path.isfile(path):
        ext = os.path.splitext(path)[1]
        if ext == ".py":
            deps = getDependenciesOfPythonFile(path)
        elif ext == ".zcml":
            deps = getDependenciesOfZCMLFile(path)
        else:
            print >>sys.stderr, ("dependencies can only be"
                                 " extracted from Python and ZCML files")
            sys.exit(1)

    else:
        print >>sys.stderr, path, "does not exist"
        sys.exit(1)

    return deps


def getCleanedDependencies(path, zcml=False):
    """Return clean dependency list."""
    deps = getDependencies(path, zcml)
    deps = filterStandardModules(deps)
    deps = filterLocalModules(deps, path)
    deps = filterMostGeneral(deps)
    deps = makeUnique(deps)
    deps.sort()
    return deps


def getAllCleanedDependencies(path, zcml=False, deps=None, paths=None):
    """Return a list of all cleaned dependencies in a path."""
    # zope and zope/app are too general to be considered.
    if path.endswith('src/zope/') or path.endswith('src/zope/app/'):
        return deps

    if deps is None:
        deps = []
        paths = []

    newdeps = getCleanedDependencies(path)
    for dep in newdeps:
        if dep.path not in paths:
            deps.append(dep)
            paths.append(dep.path)
            modulePath = __import__(dep.path).__file__
            dirname, basename = os.path.split(modulePath)
            if basename in ('__init__.py', '__init__.pyc', '__init__.pyo'):
                modulePath = os.path.join(dirname, '')
            getAllCleanedDependencies(modulePath, zcml, deps, paths)
    deps = filterMostGeneral(deps)
    deps.sort()
    return deps


def showDependencies(path, zcml=False, long=False, all=False):
    """Show the dependencies of a module on the screen."""
    if all:
        deps = getAllCleanedDependencies(path, zcml)
    else:
        deps = getCleanedDependencies(path, zcml)

    if long:
        print '='*(8+len(path))
        print "Module: " + path
        print '='*(8+len(path))
    for dep in deps:
        print dep.path
        if long:
            print '-'*len(dep.path)
            for file, lineno in dep.occurences:
                file = stripZopePrefix(file)
                if len(file) >= 69:
                    file = '...' + file[:69-3]
                print '  %s, Line %s' %(file, lineno)
            print


def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        opts, args = getopt.getopt(
            argv[1:],
            'd:m:ahlz',
            ['all', 'help', 'dir=', 'module=', 'long', 'zcml'])
    except getopt.error, msg:
        usage(1, msg)

    all = False
    long = False
    path = None
    zcml = False
    for opt, arg in opts:
        if opt in ('-a', '--all'):
            all = True
        elif opt in ('-h', '--help'):
            usage(0)
        elif opt in ('-l', '--long'):
            long = True
        elif opt in ('-d', '--dir'):
            cwd = os.getcwd()
            # This is for symlinks. Thanks to Fred for this trick.
            if os.environ.has_key('PWD'):
                cwd = os.environ['PWD']
            path = os.path.normpath(os.path.join(cwd, arg))
        elif opt in ('-m', '--module'):
            try:
                module = __import__(arg, globals(), locals(), ('something',))
                path = os.path.dirname(module.__file__)
            except ImportError:
                usage(1, "Could not import module %s" % module)
        elif opt in ('-z', '--zcml'):
            zcml = True
    if path is None:
        usage(1, 'The module must be specified either by path, '
              'dotted name or ZCML file.')
    showDependencies(path, zcml, long, all)


if __name__ == '__main__':
    main()
