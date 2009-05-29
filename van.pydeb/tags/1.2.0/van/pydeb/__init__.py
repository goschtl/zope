##############################################################################
#
# Copyright (c) 2008 Vanguardistas and Contributors.
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
import sys
import os.path
import optparse

from pkg_resources import PathMetadata, Distribution
from pkg_resources import component_re # Is this a public interface?

_HERE = os.path.dirname(__file__)

#
# Command Line Interface
#

_COMMANDS = {}

def main(argv=sys.argv):
    # Handle global options and dispatch the command 
    assert len(argv) >= 2, "You need to specify a command"
    command = _COMMANDS.get(argv[1])
    if command is None:
        raise Exception("No Command: %s" % argv[1])
    return command(argv)

#
# Package name conversion
#

# An attempt at a cannonical list of translations
def _read_map(file):
    map = {}
    reverse_map = {}
    try:
        f = open(file, 'r')
        for line in f.readlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            k, v = line.split()
            assert k not in map, "Duplicate key %s already in map. File %s" % (k, file)
            map[k] = v
            assert v not in reverse_map, "Duplicate key %s already in reverse map. File %s" % (v, file)
            reverse_map[v] = k
    finally:
        f.close()
    return map, reverse_map

_PY_TO_BIN, _BIN_TO_PY = _read_map(os.path.join(_HERE, 'py_to_bin.txt'))
_PY_TO_SRC, _SRC_TO_PY = _read_map(os.path.join(_HERE, 'py_to_src.txt'))

def py_to_bin(setuptools_project):
    """Convert a setuptools project name to a debian binary package name"""
    return _PY_TO_BIN.get(setuptools_project, 'python-%s' % setuptools_project.lower())

def py_to_src(setuptools_project):
    """Convert a setuptools project name to a debian source package name"""
    return _PY_TO_SRC.get(setuptools_project, setuptools_project.lower())

def bin_to_py(binary_package):
    """Convert a doebian binary package name to a setuptools project name"""
    py_package_name = _BIN_TO_PY.get(binary_package)
    if py_package_name is not None:
        return py_package_name
    assert binary_package.startswith('python-')
    return binary_package[7:]

def src_to_py(source_package):
    """Convert a debian source package name to a setuptools project name"""
    return _SRC_TO_PY.get(source_package, source_package)

def _string_command(argv):
    command = argv[1]
    parser = optparse.OptionParser(usage="usage: %%prog %s argument" % command)
    options, args = parser.parse_args(argv)
    assert len(argv) == 3, "Too many or few arguments"
    print {'py_to_src': py_to_src,
           'py_to_bin': py_to_bin,
           'bin_to_py': bin_to_py,
           'src_to_py': src_to_py,
           'py_version_to_deb': py_version_to_deb}[command](argv[2])
    return 0
_COMMANDS['py_to_src'] = _COMMANDS['py_to_bin'] = _string_command
_COMMANDS['src_to_py'] = _COMMANDS['bin_to_py'] = _string_command
_COMMANDS['py_version_to_deb'] = _string_command

#
# Version Conversion
#


def py_version_to_deb(version):
    """Converts an egg version to debian format to preserve sorting rules.

    We try to convert egg versions to debian versions here in a way that
    preserves sorting rules and takes into account egg ideosynchracies. We also
    try to maintain readability of the version numbers and so do not aim for
    perfection (It's highly doubtful we could attain it anyway).

    For a simple and nasty example:

        >>> py_version_to_deb('2.8.0')
        '2.8.0'
        >>> py_version_to_deb('2.8.0pre1')
        '2.8.0~c~pre1'

    """
    version = version.lower()
    result = []
    for part in component_re.split(version):
        if not part or part.isdigit() or part == '.' or part == '-':
            result.append(part)
            continue
        result.append('~')
        if part in ['pre', 'preview', 'rc']:
            # ok. so because of the way setuptools does this, we can't manage to preserve the original
            # version number and maintain sort order
            result.append('c~')
        if part == 'dev':
            result.append('~')
        result.append(part)
    return ''.join(result)

#
# Dependency Conversion
#

_setuptools_debian_operators = {'>=': '>=',
                                '>': '>>',
                                '<': '<<',
                                '==': '=',
                                '!=': None, # != not supported by debian, use conflicts in future for this
                                '<=': '<='}

def _depends_or_provides(argv):
    """Run the dependency calculation program.

        >>> import os
        >>> here = os.path.dirname(__file__)
        >>> ex1 = os.path.join(here, 'tests', 'dummy.foo.egg-info')
        >>> exitcode = main(['bin', 'depends', '--egg-info', ex1])
        python-bar (<< 0.3~c~pre1), python-dummy, python-foo (>> 0.1), python-foobar
        >>> exitcode
        0
    """
    parser = optparse.OptionParser(usage="usage: %prog command [options]")
    parser.add_option("--egg-info", dest="egg_info",
                      help="The egg-info directory to use.")
    parser.add_option("--exclude-extra", dest="exclude_extras", action="append",
                      help="Exclude extras from dependencies")
    parser.add_option("--extra", dest="extras", action="append",
                      help="Generate dependency for extra[s]")
    options, args = parser.parse_args(argv)
    assert len(args) == 2, "One and only one command can be specified"
    command = args[1]
    assert os.path.exists(options.egg_info), "Does not exist: %s" % options.egg_info
    if command == 'depends':
        deps = _get_debian_dependencies(options.egg_info, extras=options.extras, exclude_extras=options.exclude_extras)
        print ', '.join(sorted(deps))
    elif command == 'provides':
        deps = _get_debian_provides(options.egg_info, extras=options.extras, exclude_extras=options.exclude_extras)
        print ', '.join(sorted(deps))
    else:
        raise Exception("Unknown command: %s" % command)
    return 0
_COMMANDS['depends'] = _COMMANDS['provides'] = _depends_or_provides

def _get_debian_provides(file, extras=None, exclude_extras=None):
    # get provides for extras
    pydeps = set([])
    base_dir = os.path.dirname(file)
    metadata = PathMetadata(base_dir, file)
    dist = Distribution.from_filename(file, metadata=metadata)
    if exclude_extras is not None:
        assert extras is None
        extras = set(dist.extras) - set(exclude_extras)
    if extras is None:
        extras = set(dist.extras)
    for i in extras:
        pydeps.add('%s-%s' % (py_to_bin(dist.project_name), i))
    return pydeps

def _get_debian_dependencies(file, extras=None, exclude_extras=None):
    """Returns a list of the format of the dpkg dependency info."""
    pydeps = set([])
    base_dir = os.path.dirname(file)
    metadata = PathMetadata(base_dir, file)
    dist = Distribution.from_filename(file, metadata=metadata)
    included_extras = set(dist.extras)
    if exclude_extras is not None:
        included_extras = included_extras - set(exclude_extras)
    if extras is not None:
        assert exclude_extras is None
        included_extras = extras
    for req in dist.requires(extras=included_extras):
        bin_pkg = py_to_bin(req.project_name)
        pkgs = []
        for extra in req.extras:
            pkgs.append('%s-%s' % (bin_pkg, extra))
        if not pkgs:
            pkgs = [bin_pkg]
        for pkg in pkgs:
            if req.specs:
                for spec in req.specs:
                    op, version = spec
                    op = _setuptools_debian_operators[op]
                    if op is None:
                        continue
                    dpkg_version = py_version_to_deb(version)
                    pydeps.add('%s (%s %s)' % (pkg, op, dpkg_version))
            else:
                pydeps.add(pkg)
    # Let's depend on the namespace pacakges as well.
    # this is a pretty ugly way to get __init__.py into the namespace packages
    # which seems to be necessary.
    # though testing it out on ubuntu gutsy said it wasnt, it was on Debian etch
    #
    # Perhaps we could remove this a bit later
    namespace_pkgs = dist._get_metadata('namespace_packages.txt')
    for pkg in namespace_pkgs:
        bin_pkg = py_to_bin(pkg)
        pydeps.add(bin_pkg)
    if extras is not None:
        # only give the dependencies of the metapackage
        pydeps = pydeps - _get_debian_dependencies(file, exclude_extras=dist.extras)
    return pydeps
