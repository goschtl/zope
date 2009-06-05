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

from vanguardistas.pydebdep import translator

setuptools_debian_operators = {'>=': '>=',
                               '>': '>>',
                               '<': '<<',
                               '==': '=',
                               '!=': None, # != not supported by debian, use conflicts in future for this
                               '<=': '<='}

def parse_args(argv):
    """Parse the command line arguments"""
    parser = optparse.OptionParser(usage="usage: %prog [options]")
    parser.add_option("--egg_info", dest="egginfo",
                      help="The egg-info directory to use.")
    parser.add_option("--depends", dest="depends", action="store_true",
                      help="Print a Depends: line to stout", default=False)
    parser.add_option("--conflicts", dest="conflicts", action="store_true",
                      help="Print a Conflicts: line to stout", default=False)
    options, args = parser.parse_args(argv)
    assert len(args) == 1, args
    assert options.depends ^ options.conflicts
    assert os.path.exists(options.egginfo), options.egginfo
    return options

def get_debian_dependencies(file):
    """Returns a list of the format of the dpkg dependency info."""
    pydeps = []
    base_dir = os.path.dirname(file)
    metadata = PathMetadata(base_dir, file)
    dist = Distribution.from_filename(file, metadata=metadata)
    tr = translator.PackageNameTranslator()
    dist.requires()
    for req in dist.requires():
        bin_pkg = tr.egg_to_binary(req.project_name)
        if req.specs:
            for spec in req.specs:
                op, version = spec
                op = setuptools_debian_operators[op]
                if op is None:
                    continue
                dpkg_version = translator.egg_to_deb(version)
                pydeps.append('%s (%s %s)' % (bin_pkg, op, dpkg_version))
        else:
            pydeps.append(bin_pkg)
    # Let's depend on the namespace pacakges as well.
    # this is a pretty ugly way to get __init__.py into the namespace packages
    # which seems to be necessary.
    # though testing it out on ubuntu gutsy said it wasnt, it was on Debian etch
    #
    # Perhaps we could remove this a bit later
    namespace_pkgs = dist._get_metadata('namespace_packages.txt')
    for pkg in namespace_pkgs:
        bin_pkg = tr.egg_to_binary(pkg)
        pydeps.append(bin_pkg)
    return pydeps

def deps(argv=sys.argv):
    """Run the dependency calculation program.

        >>> import os
        >>> here = os.path.dirname(__file__)
        >>> ex1 = os.path.join(here, 'tests', 'dummy.foo.egg-info')
        >>> exitcode = deps(['bin', '--egg_info', ex1, '--depends'])
        python-foo (>> 0.1), python-foobar, python-bar (<< 0.3~c~pre1), python-dummy
        >>> exitcode
        0

        >>> exitcode = deps(['bin', '--egg_info', ex1, '--conflicts'])
        <BLANKLINE>
        >>> exitcode
        0
    """
    options = parse_args(argv)
    if options.conflicts:
        print ''
        return 0
    if options.depends:
        print ', '.join(get_debian_dependencies(options.egginfo))
        return 0
    return 1
