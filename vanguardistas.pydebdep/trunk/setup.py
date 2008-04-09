##############################################################################
#
# Copyright (c) 2008 Vanguardistas and Contributors.
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
from setuptools import setup, find_packages

rules = [os.path.join('rules', f) for f in os.listdir('rules') if not f.startswith('.')]

long_description = open('README.txt', 'r').read()

setup(name="vanguardistas.pydebdep",
      description='Make egg dependency information available for Debian packaging',
      long_description=long_description,
      author="Vanguardistas",
      url='http://pypi.python.org/pypi/vanguardistas.pydebdep',
      version='0.1.0dev',
      license = 'ZPL 2.1',
      packages=find_packages('src'),
      scripts=['pydebdep'],
      data_files=[('rules', rules)],
      namespace_packages=["vanguardistas"],
      package_dir = {'': 'src'},
      install_requires=[
          'setuptools',
          ],
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'Intended Audience :: System Administrators',
                   'Topic :: System :: Archiving :: Packaging',
                   'License :: DFSG approved',
                   'License :: OSI Approved :: Zope Public License',
                   'Framework :: Setuptools Plugin',
                   'Operating System :: POSIX :: Linux',
                   'Programming Language :: Python',
                   ],
      include_package_data = True,
      zip_safe = False,
      )
