##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""Protection of builtin objects.

$Id$
"""
import sys

def RestrictedBuiltins():

    from zope.security.proxy import ProxyFactory
    from zope.security.checker import NamesChecker

    # It's better to say what is safe than it say what is not safe
    _safe = [
        'ArithmeticError', 'AssertionError', 'AttributeError',
        'DeprecationWarning', 'EOFError', 'Ellipsis', 'EnvironmentError',
        'Exception', 'FloatingPointError', 'IOError', 'ImportError',
        'IndentationError', 'IndexError', 'KeyError', 'KeyboardInterrupt',
        'LookupError', 'MemoryError', 'NameError', 'None', 'NotImplemented',
        'NotImplementedError', 'OSError', 'OverflowError', 'OverflowWarning',
        'ReferenceError', 'RuntimeError', 'RuntimeWarning', 'StandardError',
        'StopIteration', 'SyntaxError', 'SyntaxWarning', 'SystemError',
        'SystemExit', 'TabError', 'TypeError', 'UnboundLocalError',
        'UnicodeError', 'UserWarning', 'ValueError', 'Warning',
        'ZeroDivisionError',
        '__debug__', '__doc__', '__name__', 'abs', 'apply', 'bool',
        'buffer', 'callable', 'chr', 'classmethod', 'cmp', 'coerce',
        'compile', 'complex', 'copyright', 'credits', 'delattr',
        'dict', 'divmod', 'eval', 'filter', 'float', 'getattr',
        'globals', 'hasattr', 'hash', 'hex', 'id', 'int', 'isinstance',
        'issubclass', 'iter', 'len', 'license', 'list', 'locals',
        'long', 'map', 'max', 'min', 'object', 'oct', 'ord', 'pow',
        'property', 'quit', 'range', 'reduce', 'repr', 'round',
        'setattr', 'slice', 'staticmethod', 'str', 'super', 'tuple',
        'type', 'unichr', 'unicode', 'vars', 'xrange', 'zip',
        'True', 'False'
        ]

    # XXX dir segfaults with a seg fault due to a bas tuple check in
    # merge_class_dict in object.c. The assert macro seems to be doing
    # the wrong think. Basically, if an object has bases, then bases
    # is assumed to be a tuple.

    # Anything that accesses an external file is a no no:
    # 'open', 'execfile', 'file'

    # We dont want restricted code to call exit: 'SystemExit', 'exit'

    # Other no nos:
    #    help prints
    #    input does I/O
    #    raw_input does I/O
    #    intern's effect is too global
    #    reload does import, XXX doesn't it use __import__?

    _builtinTypeChecker = NamesChecker(
        ['__str__', '__repr__', '__name__', '__module__',
         '__bases__', '__call__'])

    import __builtin__

    builtins = {}
    for name in _safe:
        value = getattr(__builtin__, name)
        if isinstance(value, type):
            value = ProxyFactory(value, _builtinTypeChecker)
        else:
            value = ProxyFactory(value)
        builtins[name] = value

    def __import__(name, globals=None, locals=None, fromlist=()):
        # Waaa, we have to emulate __import__'s weird semantics.
        try:
            module = sys.modules[name]
            if fromlist:
                return module

            l = name.find('.')
            if l < 0:
                return module

            return sys.modules[name[:l]]

        except KeyError:
            raise ImportError(name)

    builtins['__import__'] = ProxyFactory(__import__)

    return builtins

RestrictedBuiltins = RestrictedBuiltins()
