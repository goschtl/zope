##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
"""Takes a Zope 3 tree checkout, and updates the SVN externals based on the
controlled packages list.

Usage: update-tree [path-to-controlled-packages.cfg] [Zope3-Tree-Path]
"""
import os, sys, popen2
from zope.kgs import kgs

SVN_TEMPLATE = 'svn://svn.zope.org/repos/main/%s/tags/%s/%s'
PROPGET_TEMPLATE = 'svn propget svn:externals %s'
PROPSET_TEMPLATE = 'svn propset svn:externals "%s" %s'

def getZODBSubPackage(package, versions):
    version = versions['ZODB3']
    return SVN_TEMPLATE %('ZODB', version, 'src/'+package)

def getTwistedPackage(package, versions):
    return ('svn://svn.twistedmatrix.com/svn/Twisted/tags/releases/'
            'twisted-core-2.5.0/twisted')

def getDocutilsPackage(package, versions):
    return SVN_TEMPLATE %(package, '0.4.0', '')

def getZConfigPackage(package, versions):
    return SVN_TEMPLATE %(package, versions[package], 'ZConfig')

SPECIAL_CASES = {
    'BTrees': getZODBSubPackage,
    'persistent': getZODBSubPackage,
    'ThreadedAsync': getZODBSubPackage,
    'transaction': getZODBSubPackage,
    'ZEO': getZODBSubPackage,
    'ZODB': getZODBSubPackage,
    'twisted': getTwistedPackage,
    'docutils': getDocutilsPackage,
    'ZConfig': getZConfigPackage,
    }

def do(cmd):
    print cmd
    stdout, stdin = popen2.popen2(cmd)
    return stdout.read()

def main(args=None):
    if args is None:
        args = sys.argv[1:]

    if len(args) < 2:
        print __file__.__doc__
        sys.exit(1)

    cp_path = args[0]
    tree_path = args[1]

    pkg_versions = dict([
        (pkg.name, pkg.versions[-1])
        for pkg in kgs.KGS(cp_path).packages
        ])

    for prefix, subpath in (('', ('src',)),
                            ('zope.', ('src', 'zope')),
                            ('zope.app.', ('src', 'zope', 'app')),
                            ):
        src_path = os.path.join(tree_path, *subpath)
        packages = [
            line.split(' ')[0]
            for line in do(PROPGET_TEMPLATE %src_path).split('\n')
            if line]

        result = []
        for pkg in packages:
            fullpkg = prefix + pkg
            if fullpkg in SPECIAL_CASES:
                result.append(
                    pkg + ' ' + SPECIAL_CASES[fullpkg](pkg, pkg_versions))
            elif fullpkg in pkg_versions:
                result.append(
                    pkg +
                    ' ' +
                    SVN_TEMPLATE %(prefix+pkg, pkg_versions[fullpkg],
                                   '/'.join(subpath) + '/' + pkg))
            else:
                print fullpkg + ' skipped.'

        do(PROPSET_TEMPLATE %('\n'.join(result), src_path))
