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
#
# This file is necessary to make this directory a package.

# XXX Evil monkey patch of weakref to avoid a Python 2.3.3 weakref bug that
# causes sporadic segfaults

def monkey_patch():
    import weakref
    import gc
    ref = weakref.ref
    disable = gc.disable
    enable = gc.enable
    def monkey_ref(*args, **kw):
        disable()
        r = ref(*args, **kw)
        enable()
        return r

    weakref.ref = monkey_ref

monkey_patch()
del monkey_patch
