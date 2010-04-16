##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
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

import monkeys

# Functions moved here from the zope specific doctest module:
import inspect
import os
import sys
def _normalize_module(module, depth=2):
    """
    Return the module specified by `module`.  In particular:
      - If `module` is a module, then return module.
      - If `module` is a string, then import and return the
        module with that name.
      - If `module` is None, then return the calling module.
        The calling module is assumed to be the module of
        the stack frame at the given depth in the call stack.
    """
    if inspect.ismodule(module):
        return module
    elif isinstance(module, (str, unicode)):
        return __import__(module, globals(), locals(), ["*"])
    elif module is None:
        return sys.modules[sys._getframe(depth).f_globals['__name__']]
    else:
        raise TypeError("Expected a module, string, or None")

def _module_relative_path(module, path):
    if not inspect.ismodule(module):
        raise TypeError('Expected a module: %r' % module)
    if path.startswith('/'):
        raise ValueError('Module-relative files may not have absolute paths')

    # Find the base directory for the path.
    if hasattr(module, '__file__'):
        # A normal module/package
        basedir = os.path.split(module.__file__)[0]
    elif module.__name__ == '__main__':
        # An interactive session.
        if len(sys.argv)>0 and sys.argv[0] != '':
            basedir = os.path.split(sys.argv[0])[0]
        else:
            basedir = os.curdir
    else:
        # A module w/o __file__ (this includes builtins)
        raise ValueError("Can't resolve paths relative to the module " +
                         module + " (it has no __file__)")

    # Combine the base directory and the path.
    return os.path.join(basedir, *(path.split('/')))
