##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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

import sys

def load_compat(modname, globals):
    args = sys.version_info[:2] + (modname,)
    compatpkg = 'pythonlib.compat%d%d.%s' % args
    for pkgname in (compatpkg, modname):
        try:
            __import__(pkgname)
            mod = sys.modules[pkgname]
            break
        except ImportError:
            pass
    else:
        raise

    try:
        all = mod.__all__
    except AttributeError:
        all = [name for name in dir(mod) if not name.startswith('_')]

    for attr in all:
        globals[attr] = getattr(mod, attr)
