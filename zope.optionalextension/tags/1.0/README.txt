``zope.optionalextension`` README
=================================

This package provides a distutils extension for building optional C
extensions.  It is intended for use in projects which have a Python reference
implementation of one or more features, and which can function without
needing any C extensions to be successfully compiled.

Using the Command
-----------------

In the ``setup.py`` for your package::

  from distutils import setup # or setuptools
  from zope.optionalextension import optional_build_ext

  setup(name='your.package',
        ...
        cmdclass = {'build_ext': optional_build_ext,
                    },
        ...
       )
