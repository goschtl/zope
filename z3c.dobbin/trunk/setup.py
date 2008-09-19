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

def read(*files):
    return "\n".join((open(f).read() for f in files))

setup(name='z3c.dobbin',
      version='0.4dev',
      license='ZPL',
      author = "Malthe Borch, Stefan Eletzhofer and the Zope Community",
      author_email = "zope-dev@zope.org",
      description="Relational object persistance framework",
      long_description=read(
          'README.txt',
          'docs/DEVELOPER.txt',
          'src/z3c/dobbin/README.txt',
          'CHANGES.txt'),
      keywords='zope orm persistence',
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
            'pysqlite==2.4.1',
            ],
        ),
      install_requires = [ 'setuptools',
                           'zope.interface',
                           'zope.schema',
                           'zope.component',
                           'zope.dottedname',
                           'zope.configuration',
                           'z3c.saconfig',
                           'transaction',
                           'monkey',
                           'SQLAlchemy>=0.5.0beta2'],
      )
