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
