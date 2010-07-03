``zope.optionalextension`` README
=================================

This package provides a distutils extension for building optional C
extensions.  It is intended for use in projects which have a Python reference
implementation of one or more features, and which can function without
needing any C extensions to be successfully compiled.

Using the Command with bare ``distutils``
-----------------------------------------

In the ``setup.py`` for your package::

  from distutils.core import setup

  setup(name='your.package',
        ...
        command_packages = ['zope.optionalextension',
                            'distutils.command',
                           ]
        ...
       )

You need to ensure that ``zope.optionalextension`` is installed first
yourself.


Using the Command with bare ``setuptools``
------------------------------------------

In the ``setup.py`` for your package::

  from setuptools import setup 

  setup(name='your.package',
        ...
        setup_requires=['zope.optionalextension'],
        command_packages=['zope.optionalextension',
                          'distutils.command',
                         ]
        ...
       )
