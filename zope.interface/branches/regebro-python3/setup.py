##############################################################################
#
# Copyright (c) 2004-2007 Zope Corporation and Contributors.
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
"""Setup for zope.interface package

$Id$
"""

import os, sys

try:
    from setuptools import setup, Extension, Feature
except ImportError:
    # do we need to support plain distutils for building when even
    # the package itself requires setuptools for installing?
    from distutils.core import setup, Extension

    if sys.version_info[:2] >= (2, 4):
        extra = dict(
            package_data={
                'zope.interface': ['*.txt'],
                'zope.interface.tests': ['*.txt'],
                }
            )
    else:
        extra = {}

else:
    codeoptimization = Feature("Optional code optimizations",
                               standard = True,
                               ext_modules = [Extension(
                                             "zope.interface._zope_interface_coptimizations",
                                             [os.path.normcase(
                                             os.path.join('src', 'zope',
                                             'interface',
                                             '_zope_interface_coptimizations.c')
                                             )]
                                             )])
    extra = dict(
        namespace_packages=["zope"],
        include_package_data = True,
        zip_safe = False,
        tests_require = [],
        install_requires = ['setuptools'],
        extras_require={'docs': ['z3c.recipe.sphinxdoc']},
        features = {'codeoptimization': codeoptimization}
        )

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description=(
        read('README.txt')
        + '\n' +
        'Detailed Documentation\n'
        '**********************\n'
        + '\n.. contents::\n\n' +
        read('src', 'zope', 'interface', 'README.txt')
        + '\n' +
        read('src', 'zope', 'interface', 'adapter.txt')
        + '\n' +
        read('src', 'zope', 'interface', 'human.txt')
        + '\n' +
        read('CHANGES.txt')
        + '\n' +
        'Download\n'
        '********\n'
        )

try: # Zope 3 setuptools versions
    from build_ext_3 import build_py_2to3 as build_py
    from build_ext_3 import optional_build_ext
    from build_ext_3 import test_2to3 as test
    # This is Python 3. Setuptools is now required, and so is zope.fixers.
    extra['install_requires'] = ['setuptools', 'zope.fixers' ],

except (ImportError, SyntaxError):
    try: # Zope 2 setuptools versions
        from setuptools.command.build_py import build_py
        from setuptools.command.test import test
        from build_ext_2 import optional_build_ext
    except ImportError:
        # Zope 2 distutils
        from distutils.command.build_py import build_py
        from distutils.command.test import test
        from build_ext_2 import optional_build_ext
    
setup(name='zope.interface',
      version = '3.5.2dev',
      url='http://pypi.python.org/pypi/zope.interface',
      license='ZPL 2.1',
      description='Interfaces for Python',
      author='Zope Corporation and Contributors',
      author_email='zope-dev@zope.org',
      long_description=long_description,

      packages = ['zope', 'zope.interface', 'zope.interface.tests'],
      package_dir = {'': 'src'},
      cmdclass = {'build_ext': optional_build_ext,
                  'build_py': build_py,
                  'test': test,
                  },
      test_suite = 'zope.interface.tests',
      **extra)
