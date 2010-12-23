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
"""Setup for zope.ucol package

$Id$
"""

import os, sys

from distutils.core import setup, Extension

try:
    from setuptools import setup, Extension
except:
    setuptools_options = {}
else:

    setuptools_options = dict(
        install_requires=['setuptools'],
        namespace_packages=['zope'],
        zip_safe = False,
        include_package_data = True,
        )

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

if sys.platform.startswith('win'):
    libraries = ['icuin', 'icuuc', 'icudt']
else:
    libraries=['icui18n', 'icuuc', 'icudata']

name = 'zope.ucol'
setup(name=name,
      version='1.0.2',
      author = "Jim Fulton",
      author_email = "jim@zope.com",
      description = "Python access to ICU text collation",
      long_description=(
        read('README.txt')
        + '\n' +
        read('CHANGES.txt')
        + '\n' +
        read('INSTALL.txt')
        + '\n' +
        'Detailed Documentation\n'
        '**********************\n'
        + '\n' +
        read('src', 'zope', 'ucol', 'README.txt')
        + '\n' +
        'Download\n'
        '**********************\n'
        ),
      license = "ZPL 2.1",
      keywords = "internationalization",
      url = 'http://www.python.org/pypi/zope.ucol',
      ext_modules=[
          Extension('zope.ucol._zope_ucol',
                    ['src/zope/ucol/_zope_ucol.c'],
                    libraries=libraries,
           )
          ],
      packages=["zope", "zope.ucol"],
      package_dir = {'': 'src'},
      classifiers = [
       'Development Status :: 5 - Production/Stable',
       'Intended Audience :: Developers',
       'License :: OSI Approved :: Zope Public License',
       'Topic :: Software Development :: Libraries :: Python Modules',
       'Topic :: Software Development :: Internationalization',
       ],

      **setuptools_options)
