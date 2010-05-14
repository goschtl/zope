##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
import commands
import fnmatch
import optparse
import os
import sys
import xml.sax.handler

import pkg_resources

from z3c.dependencychecker import importchecker


def print_unused_imports(unused_imports):
    found = []
    for path in unused_imports.keys():
        for (module, line_number) in unused_imports[path]:
            found.append((path, line_number, module))
    if found:
        print "Unused imports"
        print "=============="
        for (path, line_number, module) in sorted(found):
            print "%s:%s:  %s" % (path, line_number, module)
        print


def name_from_setup():
    os.environ['PYTHONPATH'] = ':'.join(sys.path)
    cmd = "%s setup.py --name" % sys.executable
    name = commands.getoutput(cmd).strip()
    if 'traceback' in name.lower():
        print "You probably don't have setuptools installed globally"
        print "Or there's an error in your setup.py."
        print "Try running this by hand:"
        print cmd
        # Use buildout's setuptools_loc environ hack.
        sys.exit(1)
    return name


def existing_requirements():
    """Extract install and test requirements"""
    name = name_from_setup()
    # Who on earth made it so earth-shattering impossible to get your hands on
    # the egg info stuff via an api?  We'll do it mostly by hand...
    egginfo_dir_name = name + '.egg-info'
    if egginfo_dir_name in os.listdir(os.getcwd()):
        egginfo_dir = egginfo_dir_name
    else:
        egginfo_dir = os.path.join(os.getcwd(), 'src', egginfo_dir_name)
    requires_filename = os.path.join(egginfo_dir, 'requires.txt')
    if not os.path.exists(requires_filename):
        print "No %s found, exiting" % requires_filename
        sys.exit(1)
    lines = [line.strip() for line in open(requires_filename).readlines()]
    lines = [line for line in lines if line]
    install_required = set()
    test_required = set()
    for line in lines:
        if line.startswith('['):
            break
        req = pkg_resources.Requirement.parse(line)
        install_required.add(req.project_name)
    start = False
    for line in lines:
        if line == '[test]':
            start = True
            continue
        if not start:
            continue
        if line.startswith('['):
            break
        req = pkg_resources.Requirement.parse(line)
        test_required.add(req.project_name)

    # The project itself is of course both available and needed.
    install_required.add(name)

    # Distribute says it is setuptools.  Setuptools also includes
    # pkg_resources.
    if 'distribute' in install_required:
        install_required.add('setuptools')
    if 'setuptools' in install_required:
        install_required.add('pkg_resources')

    return (install_required, test_required)


def filter_missing(imports, required):
    missing = set()
    for needed in imports:
        found = False
        for req in required:
            if req.lower() == needed.lower():
                found = True
            if needed.lower().startswith(req.lower() + '.'):
                # 're' should not match 'reinout.something', that's why we
                # check with an extra dot.
                found = True
        if not found:
            missing.add(needed)
    missing = set(missing)
    return missing


def filter_unneeded(imports, required):
    name = name_from_setup()
    imports.add(name) # We always use ourselves, obviously.
    setuptools_and_friends = set(
        ['distribute', 'setuptools', 'pkg_resources'])
    required = required - setuptools_and_friends

    unneeded = set()
    for req in required:
        found = False
        for module in imports:
            if module.lower().startswith(req.lower()):
                found = True
        if not found:
            unneeded.add(req)
    return unneeded


def _detect_modules(sample_module):
    sample_file = os.path.realpath(sample_module.__file__)
    stdlib_dir = os.path.dirname(sample_file)
    stdlib_extension = os.path.splitext(sample_file)[1]
    stdlib_files = os.listdir(stdlib_dir)
    modules = []
    for stdlib_file in stdlib_files:
        module, extension = os.path.splitext(stdlib_file)
        if extension == stdlib_extension:
            modules.append(module)
    if 'py' in stdlib_extension:
        # Also check directories with __init__.py* in them.
        init_file = '__init__' + stdlib_extension
        extra_modules = [name for name in os.listdir(stdlib_dir)
                         if os.path.exists(os.path.join(
                             stdlib_dir, name, init_file))]
        modules += extra_modules
    return modules


def stdlib_modules():
    py_module = os
    import datetime
    dynload_module = datetime
    modules = _detect_modules(py_module) + _detect_modules(dynload_module)
    modules.append('sys')
    return set(modules)


def get_import_name(path, _cache={}):
    import_name = _cache.get(path)
    if import_name is not None:
        return import_name
    # Determine the name of the module/package.
    parts = []
    if os.path.isfile(path):
        path, modulefn = os.path.split(path)
        parts.append(os.path.splitext(modulefn)[0])
    while os.path.isfile(os.path.join(path, '__init__.py')):
        path, name = os.path.split(path)
        parts.append(name)
    import_name = '.'.join(reversed(parts))
    _cache[path] = import_name
    return import_name


class ZCMLDependencyParser(xml.sax.handler.ContentHandler):

    def __init__(self, packagename):
        self.dependencies = set()
        self.stack = [packagename]

    def _absolutename(self, relativename):
        assert relativename
        for pos,c in enumerate(relativename):
            if c!='.':
                break
        if pos:
            absolutename = (
                self.stack[-1].rsplit('.', pos-1)[0] + relativename[pos-1:]
                )
        else:
            absolutename = relativename
        return absolutename

    def startElement(self, tag, attrib):
        if tag == 'configure':
            package = attrib.get('package')
            if package is None:
                name = self.stack[-1]
            else:
                name = self._absolutename(package)
            self.stack.append(name)
            self.dependencies.add(name)
        else:
            for attrname in ('allowed_interface',
                             'class',
                             'component',
                             'content_factory',
                             'factory',
                             'for',
                             'handler',
                             'interface',
                             'layer',
                             'like_class',
                             'module',
                             'package',
                             'provides',
                             'schema',
                             'set_schema',
                             'type',
                             'usedIn',
                             ):
                attr = attrib.get(attrname)
                if attr is not None:
                    for name in attr.split():
                        if name!='*':
                            self.dependencies.add(self._absolutename(name))

    def endElement(self, tag):
        if tag == 'configure':
            self.stack.pop()


def includes_from_zcml(path):
    modules = set()
    test_modules = set()
    for path, dirs, files in os.walk(path):
        for zcml in [os.path.abspath(os.path.join(path, filename))
                     for filename in files
                     if fnmatch.fnmatch(filename, '*.zcml')]:
            packagename = get_import_name(path)
            target = ZCMLDependencyParser(packagename)
            xml.sax.parse(zcml, target)
            found = target.dependencies
            if 'test' in zcml:
                # ftesting.zcml, mostly.
                test_modules |= found
            else:
                modules |= found
    return modules, test_modules


def imports_from_doctests(path):
    test_modules = set()
    for path, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d!='.svn']
        for filename in [
            os.path.abspath(os.path.join(path, filename))
            for filename in files
            if fnmatch.fnmatch(filename, '*.txt')
            or fnmatch.fnmatch(filename, '*.rst')
            or fnmatch.fnmatch(filename, '*.py')]:
            module = importchecker.Module(filename, True)
            test_modules.update(module.getImportedModuleNames())
    return test_modules


def print_modules(modules, heading):
    if modules:
        print heading
        print '=' * len(heading)
        for module in sorted(modules):
            print "    ", module
        print


def determine_path(args):
    if len(args) > 0:
        path = args[0]
    else:
        # Default
        path = os.path.join(os.getcwd(), 'src')
    path = os.path.abspath(path)
    if not os.path.isdir(path):
        print "Unknown path:", path
        sys.exit(1)
    return path


def _version():
    ourselves = pkg_resources.require('z3c.dependencychecker')[0]
    return ourselves.version


def main():
    usage = "Usage: %prog [path]\n  (path defaults to 'src')"
    parser = optparse.OptionParser(usage=usage, version=_version())
    (options, args) = parser.parse_args()
    path = determine_path(args)

    db = importchecker.ImportDatabase(path)
    # TODO: find zcml files
    db.findModules()
    unused_imports = db.getUnusedImports()
    test_imports = db.getImportedModuleNames(tests=True)
    install_imports = db.getImportedModuleNames(tests=False)
    (install_required, test_required) = existing_requirements()
    stdlib = stdlib_modules()
    (zcml_imports, zcml_test_imports) = includes_from_zcml(path)
    doctest_imports = imports_from_doctests(path)

    print_unused_imports(unused_imports)

    install_missing = filter_missing(install_imports | zcml_imports,
                                     install_required | stdlib)
    print_modules(install_missing, "Missing requirements")

    test_missing = filter_missing(
        test_imports | zcml_test_imports | doctest_imports,
        install_required | test_required | stdlib)
    print_modules(test_missing, "Missing test requirements")

    install_unneeded = filter_unneeded(install_imports | zcml_imports,
                                       install_required)
    # See if one of ours is needed by the tests
    really_unneeded = filter_unneeded(
        test_imports | zcml_test_imports | doctest_imports,
        install_unneeded)
    move_to_test = install_unneeded - really_unneeded

    print_modules(really_unneeded, "Unneeded requirements")
    print_modules(move_to_test,
                  "Requirements that should be test requirements")

    test_unneeded = filter_unneeded(
        test_imports | zcml_test_imports | doctest_imports,
        test_required)
    print_modules(test_unneeded, "Unneeded test requirements")


    if install_missing or test_missing or install_unneeded or test_unneeded:
        print "Note: requirements are taken from the egginfo dir, so you need"
        print "to re-run buildout (or setup.py or whatever) for changes in"
        print "setup.py to have effect."
        print
