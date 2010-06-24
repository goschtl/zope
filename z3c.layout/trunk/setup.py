##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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

import os
from setuptools import setup, find_packages, Extension

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='z3c.layout',
      version = '0.2dev',
      description='HTML layout engine',
      long_description=read('README.txt')+read('src/z3c/layout/README.txt'),
      author = "Malthe Borch, Stefan Eletzhofer and the Zope Community",
      author_email = "zope-dev@zope.org",
      keywords = "zope3 layout HTML",
      classifiers = [
          'Development Status :: 4 - Beta',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Programming Language :: Python',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Topic :: Internet :: WWW/HTTP',
          'Framework :: Zope3'],
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['z3c', ],
      extras_require = dict(
        test = [
            'zope.app.testing',
            ],
        ),
      install_requires=['setuptools',
                        'zope.interface',
                        'zope.schema',
                        'zope.component',
                        'zope.app.publisher',
                        'zope.contentprovider',
                        'zope.viewlet',
                        'plone.memoize',
                        'lxml>=2.0',
                        ],
      include_package_data = True,
      zip_safe = False,
      )
