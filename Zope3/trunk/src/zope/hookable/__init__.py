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
"""Hookable object support

   Support the efficient creation of hookable objects, which are
   callable objects that are meant to be replaced by other callables,
   at least optionally.

   The idea is you create a function that does some default thing and
   make it hookable. Later, someone can modify what it does by calling
   it's sethook method and changing it's implementation.  All users of
   the function, including tose that imported it, will see the change.

   >>> def f41():
   ...     return 41
   >>> f = hookable(f41)
   >>> int(f.implementation is f.original)
   1
   >>> f()
   41
   >>> old = f.sethook(lambda: 42)
   >>> int(f.implementation is f.original)
   0
   >>> int(old is f41)
   1
   >>> f()
   42
   >>> f.original()
   41
   >>> f.implementation()
   42
   >>> f.reset()
   >>> f()
   41

   >>> del f.original
   Traceback (most recent call last):
     File "/usr/local/python/2.2.2/lib/python2.2/doctest.py", line 430, in _run_examples_inner
       compileflags, 1) in globs
     File "<string>", line 1, in ?
   TypeError: readonly attribute

   >>> del f.implementation
   Traceback (most recent call last):
     File "/usr/local/python/2.2.2/lib/python2.2/doctest.py", line 430, in _run_examples_inner
       compileflags, 1) in globs
     File "<string>", line 1, in ?
   TypeError: readonly attribute

   
$Id: __init__.py,v 1.1 2003/05/18 18:03:55 jim Exp $
"""
from _zope_hookable import *

# DocTest:
if __name__ == "__main__":
    import doctest, __main__
    doctest.testmod(__main__, isprivate=lambda *a: False)
