==================================
Support for Restricted Python Code
==================================

This package, `zope.restrictedpython`, provides a way to compile
untrusted Python code so that it can be executed safely.

This currently only supports expressions (compile()'s "eval" mode);
support for "exec" and "single" modes will be added later.

This form of restricted Python assumes that security proxies will be
used to protect assets.  Given this, the only thing that actually
needs to be done differently by the generated code is to ensure that
all attribute lookups go through a safe version of the getattr()
function that's been provided in the built-in functions used in the
execution environment.  No other special treatment is needed to
support safe expression evaluation.  (Additional behaviors are needed
for the "exec" and "single" modes.)

The implementation makes use of the `RestrictedPython` package,
originally written for Zope 2.  There is a new AST re-writer in
`zope.restrictedpython.mutator` which performs the
tree-transformation, and a top-level `compile()` function in
`zope.restrictedpython.rcompile`; the later is what client
applications are expected to use.

The signature of the `compile()` function is very similar to that of
Python's built-in `compile()` function::

  compile(source, filename, mode)

Using it is equally simple::

  >>> from zope.restrictedpython.rcompile import compile

  >>> code = compile("21 * 2", "<string>", "eval")
  >>> eval(code)
  42

What's interesting about the restricted code is that all attribute
lookups go through the `getattr()` function.  This is generally
provided as a built-in function in the restricted environment::

  >>> def mygetattr(object, name, default="Yahoo!"):
  ...     marker = []
  ...     print "Looking up", name
  ...     if getattr(object, name, marker) is marker:
  ...         return default
  ...     else:
  ...         return "Yeehaw!"

  >>> import __builtin__
  >>> builtins = __builtin__.__dict__.copy()
  >>> builtins["getattr"] = mygetattr

  >>> def reval(source):
  ...     code = compile(source, "README.txt", "eval")
  ...     globals = {"__builtins__": builtins}
  ...     return eval(code, globals, {})

  >>> reval("(42).__class__")
  Looking up __class__
  'Yeehaw!'
  >>> reval("(42).not_really_there")
  Looking up not_really_there
  'Yahoo!'

This allows a `getattr()` to be used that ensures the result of
evaluation is a security proxy.
