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
    -a / --a
        Find all dependencies. This means that the program will also scan the
        dependencies originally found in the module.

    -h / --help
        Print this message and exit.

    -l / --long
        If long is specified, the file and line where the dependency occurs is
        reported.

    -m / --module
        Specify the path of the module that is being inspected.

    -z / --zcml
        Also look through ZCML files for dependencies.

Important: Make sure that the PYTHONPATH is set to or includes 'ZOPE3/src'.

$Id: finddeps.py,v 1.12 2004/03/12 15:58:23 fdrake Exp $
"""
import sys
import getopt
import os
import re
import token
import tokenize

# Get the Zope base path
import zope
ZOPESRC = os.path.dirname(os.path.dirname(zope.__file__))
ZOPESRCPREFIX = os.path.join(ZOPESRC, "")

# Matching expression for python files.
pythonfile = re.compile(r'[a-zA-Z][a-zA-Z0-9_]*\.py$')
zcmlfile = re.compile(r'[a-zA-Z][a-zA-Z0-9_]*\.zcml$')

# Matching expressions of dotted paths in XML
dottedName = re.compile(r'"[a-zA-Z\.][a-zA-Z0-9_\.]*"')


def stripZopePrefix(path):
    """Remove the '.../src/' prefix from path, if present."""
    if path.startswith(ZOPESRCPREFIX):
        return path[len(ZOPESRCPREFIX):]
    else:
        return path


class Dependency(object):
    """Object representing a dependency."""

    def __init__(self, path, file, lineno):
        self.path = path
        self.occurences = [(file, lineno)]

    def addOccurence(self, file, lineno):
        """Add occurenace of the dependency in the code."""
        self.occurences.append((file, lineno))

    def isSubPackageOf(self, dep):
        """Return True if this dependency's path is a sub-package of dep."""
        path = self.path.split('.')
        deppath = dep.path.split('.')
        for i in range(len(path)):
            if i >= len(deppath):
                return True
            if path[i] != deppath[i]:
                break
        return False

    def __cmp__(self, other):
        """Compare dependecies by path."""
        return cmp(self.path, other.path)


def usage(code, msg=''):
    """Display help."""
    print >> sys.stderr, '\n'.join(__doc__.split('\n')[:-2])
    if msg:
        print >> sys.stderr, '** Error: ' + str(msg) + ' **'
    sys.exit(code)


def makePythonPath(path):
    """Make out of a patha  dotted Python path, using sys.path"""
    syspaths = sys.path[1:]
    syspaths.append(os.getcwd())
    for syspath in syspaths:
        if path.startswith(syspath):
            cutPath = path.replace(syspath+'/', '')
            dottedPath = '.'.join(cutPath.split('/'))
            return dottedPath

    raise ValueError, 'Cannot create dotted path.'


START = "<start>"
FROM = "<from>"
FROM_IMPORT = "<from-import>"
IMPORT = "<import>"
COLLECTING = "<collecting>"
SWALLOWING = "<swallowing>"  # used to swallow "as foo"

TOK_COMMA = (token.OP, ",")
TOK_IMPORT = (token.NAME, "import")
TOK_FROM = (token.NAME, "from")
TOK_NEWLINE = (token.NEWLINE, "\n")
TOK_ENDMARK = (token.ENDMARKER, "")

dotjoin = ".".join


class ImportFinder:

    def __init__(self):
        self.module_checks = {}
        self.deps = []
        self.imported_names = {}

    def get_imports(self):
        return self.deps

    def find_imports(self, f, path):
        self.path = path
        self.state = START
        self.post_name_state = None
        prevline = None
        try:
            for t in tokenize.generate_tokens(f.readline):
                type, string, start, end, line = t
                self.transition(type, string, start[0])
        except:
            print >>sys.stderr, "error finding imports in", path
            raise

    def add_import(self, name, lineno):
        if name not in self.module_checks:
            # determine if a module name, or something in a module:
            self.check_module_name(name)
            if not self.module_checks[name] and "." in name:
                # if "." isn't in name, I'd be very surprised!
                # i'd also be surprised if the result *isn't* a module
                name = dotjoin(name.split(".")[:-1])
                self.check_module_name(name)
        # A few oddball cases import __main__ (support for
        # command-line scripts), so we need to filter that out.
        if self.module_checks[name] and name != "__main__":
            self.deps.append(Dependency(name, self.path, lineno))

    def check_module_name(self, name):
        try:
            __import__(name)
        except ImportError:
            self.module_checks[name] = False
            # XXX remove the last part and check again:
        else:
            self.module_checks[name] = name in sys.modules

    def transition(self, type, string, lineno):
        entry = self.state_table.get((self.state, (type, string)))
        if entry is not None:
            self.state = entry[0]
            for action in entry[2:]:
                meth = getattr(self, "action_" + action)
                meth(type, string, lineno)
            if entry[1] is not None:
                self.post_name_state = entry[1]

        # gotta figure out what to do:
        elif self.state == COLLECTING:
            # watch for "as" used as syntax
            name = self.name
            if type == token.NAME and name and not name.endswith("."):
                self.state = SWALLOWING
                if self.prefix:
                    self.name = "%s.%s" % (self.prefix, name)
            else:
                self.name += string

        elif self.state in (START, SWALLOWING):
            pass

        else:
            raise RuntimeError(
                "invalid transition: %s %r" % (self.state, (type, string)))

    state_table = {
        # (state,     token):       (new_state,  saved_state, action...),
        (START,       TOK_IMPORT):  (COLLECTING, IMPORT, "reset"),
        (START,       TOK_FROM):    (COLLECTING, FROM,   "reset"),

        (FROM,        TOK_IMPORT):  (COLLECTING, FROM_IMPORT, "setprefix"),
        (FROM_IMPORT, TOK_COMMA):   (COLLECTING, FROM_IMPORT),
        (IMPORT,      TOK_COMMA):   (COLLECTING, IMPORT),

        (COLLECTING,  TOK_COMMA):   (COLLECTING, None,   "save", "poststate"),
        (COLLECTING,  TOK_IMPORT):  (COLLECTING, FROM_IMPORT, "setprefix"),

        (SWALLOWING,  TOK_COMMA):   (None,       None,   "save", "poststate"),

        # Commented-out transitions are syntax errors, so shouldn't
        # ever be seen in working code.

        # end of line:
        #(START,       TOK_NEWLINE): (START,      None,   "save", "reset"),
        #(FROM,        TOK_NEWLINE): (START,      None,   "save", "reset"),
        (FROM_IMPORT, TOK_NEWLINE): (START,      None,   "save", "reset"),
        #(IMPORT,      TOK_NEWLINE): (START,      None,   "save", "reset"),
        (COLLECTING,  TOK_NEWLINE): (START,      None,   "save", "reset"),
        (SWALLOWING,  TOK_NEWLINE): (START,      None,   "save", "reset"),

        # end of input:
        #(START,       TOK_ENDMARK): (START,      None,   "save", "reset"),
        #(FROM,        TOK_ENDMARK): (START,      None,   "save", "reset"),
        (FROM_IMPORT, TOK_ENDMARK): (START,      None,   "save", "reset"),
        #(IMPORT,      TOK_ENDMARK): (START,      None,   "save", "reset"),
        (COLLECTING,  TOK_ENDMARK): (START,      None,   "save", "reset"),
        (SWALLOWING,  TOK_ENDMARK): (START,      None,   "save", "reset"),
        }

    def action_reset(self, type, string, lineno):
        self.name = ''
        self.prefix = None

    def action_save(self, type, string, lineno):
        if self.name:
            assert not self.name.endswith(".")
            name = self.name
            if self.prefix:
                name = "%s.%s" % (self.prefix, name)
            self.add_import(name, lineno)
            self.name = ""

    def action_setprefix(self, type, string, lineno):
        assert self.name
        assert not self.name.endswith(".")
        self.prefix = self.name
        self.name = ""

    def action_collect(self, type, string, lineno):
        self.name += string

    def action_poststate(self, type, string, lineno):
        self.state = self.post_name_state
        self.post_name_state = None
        self.transition(type, string, lineno)


def getDependenciesOfPythonFile(path):
    finder = ImportFinder()
    finder.find_imports(open(path, 'rU'), path)
    return finder.get_imports()


def getDependenciesOfZCMLFile(path):
    """Get dependencies from ZCML file."""
    localModule = stripZopePrefix(os.path.dirname(path))
    localModule = localModule.replace('/', '.')
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
    dottedPath = makePythonPath(path)
    filteredDeps = []
    for dep in deps:
        if not dep.path.startswith(dottedPath):
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
            elif os.path.isdir(filePath) and \
                     '__init__.py' in os.listdir(filePath):
                deps += getDependencies(filePath)

    elif os.path.isfile(path):
        deps = getDependenciesOfFile(path)

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


if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            'm:ahlz',
            ['all', 'help', 'module=', 'long', 'zcml'])
    except getopt.error, msg:
        usage(1, msg)

    all = False
    long = False
    module = None
    zcml = False
    for opt, arg in opts:
        if opt in ('-a', '--all'):
            all = True
        elif opt in ('-h', '--help'):
            usage(0)
        elif opt in ('-l', '--long'):
            long = True
        elif opt in ('-m', '--module'):
            cwd = os.getcwd()
            # This is for symlinks. Thanks to Fred for this trick.
            if os.environ.has_key('PWD'):
                cwd = os.environ['PWD']
            module = os.path.normpath(os.path.join(cwd, arg))
        elif opt in ('-z', '--zcml'):
            zcml = True

    if module is None:
        usage(1, 'The module must be specified.')
    showDependencies(module, zcml, long, all)
