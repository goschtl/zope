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
    else:
        # If the original had __all__, the exported version should as
        # well, since there's no checking that it's the same as what
        # would be auto-generated from the resulting module.
        globals["__all__"] = mod.__all__

    for attr in all:
        globals[attr] = getattr(mod, attr)

    # Add the module docstring if the shim module doesn't provide one.
    if getattr(mod, "__doc__", None) and "__doc__" not in globals:
        globals["__doc__"] = mod.__doc__
