# These are all supposed to raise a SyntaxError when using
# compile_restricted() but not when using compile().
# Each function in this module is compiled using compile_restricted().

from __future__ import generators

def overrideGuardWithFunction():
    def _getattr(o): return o

def overrideGuardWithLambda():
    lambda o, _getattr=None: o

def overrideGuardWithClass():
    class _getattr:
        pass

def overrideGuardWithName():
    _getattr = None

def overrideGuardWithArgument():
    def f(_getattr=None):
        pass

def reserved_names():
    printed = ''

def bad_name():
    __ = 12

def bad_attr():
    some_ob._some_attr = 15

def no_exec():
    exec 'q = 1'

def no_yield():
    yield 42

def check_getattr_in_lambda(arg=lambda _getattr=(lambda ob, name: name):
                                       _getattr):
    42

def import_as_bad_name():
    import os as _leading_underscore

def except_using_bad_name():
    try:
        foo
    except NameError, _leading_underscore:
        # The name of choice (say, _write) is now assigned to an exception
        # object.  Hard to exploit, but conceivable.
        pass
