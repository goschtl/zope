##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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

from setuptools import setup, find_packages

setup(name='z3c.dobbin',
      version='0.2.9',
      license='ZPL',
      author = "Malthe Borch, Stefan Eletzhofer and the Zope Community",
      author_email = "zope-dev@zope.org",
      description="Relational object persistance framework",
      long_description=open('README.txt').read()+open('src/z3c/dobbin/README.txt').read(),
      keywords='',
      classifiers=['Programming Language :: Python',
                   'Environment :: Web Environment',
                   'Framework :: Zope3',
                   ],
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['z3c'],
      include_package_data=True,
      zip_safe=False,
      extras_require = dict(
        test = [
            'zope.app.testing',
            ],
        ),
      install_requires = [ 'setuptools',
                           'zope.interface',
                           'zope.schema',
                           'zope.component',
                           'zope.dottedname',
                           'ore.alchemist',
                           'ZODB3',
                           'SQLAlchemy==0.4.6'],
      )
