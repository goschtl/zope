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

    -p / --packages
        List only package names, not individual module names.

    -z / --zcml
        Also look through ZCML files for dependencies.

$Id$
"""
import errno
import getopt
import os
import re
import sys

import zope

from zope.dependencytool.dependency import Dependency
from zope.dependencytool import importfinder


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
    dirname, basename = os.path.split(path)
    basename = os.path.splitext(basename)[0]
    path = os.path.join(dirname, basename)
    syspaths = sys.path[:]
    if "" in syspaths:
        # This is the directory that contains the driver script; there
        # are no modules there.
        syspaths.remove("")
    for syspath in syspaths:
        syspath = os.path.join(syspath, '')
        if path.startswith(syspath):
            return path[len(syspath):].replace(os.sep, ".")

    raise ValueError, 'Cannot create dotted name for %r' % path


def getDependenciesOfPythonFile(path, packages):
    finder = importfinder.ImportFinder(packages)
    module_name = makeDottedName(path)
    if '.' in module_name:
        package = module_name[:module_name.rfind('.')]
    else:
        package = None
    finder.find_imports(open(path, 'rU'), path, package)
    return finder.get_imports()


def getDependenciesOfZCMLFile(path, packages):
    """Get dependencies from ZCML file."""
    s = makeDottedName(path)
    localPackage = s[:s.rfind(".")]
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
                    name = localPackage + name
                name = importfinder.module_for_importable(name)
                if packages:
                    name = importfinder.package_for_module(name)
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
            __import__(dep.name)
        except ImportError:
            continue
        module = sys.modules[dep.name]
        # built-ins (like sys) do not have a file associated
        if not hasattr(module, '__file__'):
            continue
        starts = module.__file__.startswith
        if starts(standard_lib) and not starts(site_packages):
            continue
        filteredDeps.append(dep)
    return filteredDeps


def makeUnique(deps):
    """Remove entries that appear multiple times"""
    uniqueDeps = {}
    for dep in deps:
        if dep.name in uniqueDeps:
            uniqueDeps[dep.name].addOccurence(*dep.occurences[0])
        else:
            uniqueDeps[dep.name] = dep
    return uniqueDeps.values()


def getDependencies(path, zcml=False, packages=False):
    """Get all dependencies of a package or module.

    If the path is a package, all Python source files are searched inside it.
    """
    if os.path.isdir(path):
        deps = []
        for file in os.listdir(path):
            filePath = os.path.join(path, file)
            if pythonfile.match(file):
                deps += getDependenciesOfPythonFile(filePath, packages)
            elif zcml and zcmlfile.match(file):
                deps += getDependenciesOfZCMLFile(filePath, packages)
            elif os.path.isdir(filePath):
                filenames = os.listdir(filePath)
                if (  'PUBLICATION.cfg' not in filenames
                      and 'SETUP.cfg' not in filenames
                      and 'DEPENDENCIES.cfg' not in filenames
                      and '__init__.py' in filenames):
                    deps += getDependencies(filePath, zcml, packages)

    elif os.path.isfile(path):
        ext = os.path.splitext(path)[1]
        if ext == ".py":
            deps = getDependenciesOfPythonFile(path, packages)
        elif ext == ".zcml":
            deps = getDependenciesOfZCMLFile(path, packages)
        else:
            print >>sys.stderr, ("dependencies can only be"
                                 " extracted from Python and ZCML files")
            sys.exit(1)

    else:
        print >>sys.stderr, path, "does not exist"
        sys.exit(1)

    return deps


def getCleanedDependencies(path, zcml=False, packages=False):
    """Return clean dependency list."""
    deps = getDependencies(path, zcml, packages)
    deps = filterStandardModules(deps)
    deps = makeUnique(deps)
    deps.sort()
    return deps


def getAllCleanedDependencies(path, zcml=False, deps=None, paths=None,
                              packages=False):
    """Return a list of all cleaned dependencies in a path."""
    # zope and zope/app are too general to be considered.
    # TODO: why?  dependencies are dependencies.
    # Because otherwise it would just pick up zope as a dependency, but
    # nothing else. We need a way to detect packages.
    if path.endswith('src/zope/') or path.endswith('src/zope/app/'):
        return deps

    if deps is None:
        deps = []
        paths = []

    newdeps = getCleanedDependencies(path, zcml, packages)
    for dep in newdeps:
        if dep.name not in paths:
            deps.append(dep)
            paths.append(dep.name)
            modulePath = __import__(dep.name).__file__
            dirname, basename = os.path.split(modulePath)
            if basename in ('__init__.py', '__init__.pyc', '__init__.pyo'):
                modulePath = os.path.join(dirname, '')
            getAllCleanedDependencies(modulePath, zcml, deps, paths, packages)
    deps.sort()
    return deps


def showDependencies(path, zcml=False, long=False, all=False, packages=False):
    """Show the dependencies of a module on the screen."""
    if all:
        deps = getAllCleanedDependencies(path, zcml, packages)
    else:
        deps = getCleanedDependencies(path, zcml, packages)

    if long:
        print '='*(8+len(path))
        print "Module: " + path
        print '='*(8+len(path))
    for dep in deps:
        print dep.name
        if long:
            print '-'*len(dep.name)
            for file, lineno in dep.occurences:
                file = stripZopePrefix(file)
                if len(file) >= 69:
                    file = '...' + file[:69-3]
                print '  %s, Line %s' %(file, lineno)
            print


class DependencyOptions(object):

    all = False
    long = False
    packages = False
    path = None
    zcml = False


def parse_args(argv):
    try:
        opts, args = getopt.getopt(
            argv[1:],
            'd:m:pahlz',
            ['all', 'help', 'dir=', 'module=', 'long', 'packages', 'zcml'])
    except getopt.error, msg:
        usage(1, msg)

    options = DependencyOptions()
    for opt, arg in opts:
        if opt in ('-a', '--all'):
            options.all = True
        elif opt in ('-h', '--help'):
            usage(0)
        elif opt in ('-l', '--long'):
            options.long = True
        elif opt in ('-d', '--dir'):
            cwd = os.getcwd()
            # This is for symlinks. Thanks to Fred for this trick.
            # I often sym-link directories from other locations into the Zope
            # source tree. This code is a bit Unix (or even bash) specific,
            # but it is better than nothing. If you don't like it, ignore it.
            if os.environ.has_key('PWD'):
                cwd = os.environ['PWD']
            options.path = os.path.normpath(os.path.join(cwd, arg))
        elif opt in ('-m', '--module'):
            try:
                __import__(arg)
                module = sys.modules[arg]
                options.path = os.path.dirname(module.__file__)
            except ImportError:
                usage(1, "Could not import module %s" % arg)
        elif opt in ('-p', '--packages'):
            options.packages = True
        elif opt in ('-z', '--zcml'):
            options.zcml = True
    if options.path is None:
        usage(1, 'The module must be specified either by path, '
              'dotted name or ZCML file.')
    return options


def main(argv=None):
    try:
        if argv is None:
            argv = sys.argv
        options = parse_args(argv)
        showDependencies(options.path, options.zcml, options.long,
                         options.all, options.packages)
    except IOError, e:
        # Ignore EPIPE since that really only indicates some
        # application on the other end of piped output exited early.
        if e.errno != errno.EPIPE:
            raise
    except KeyboardInterrupt:
        sys.exit(1)
