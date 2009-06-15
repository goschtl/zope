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

long_description = open(os.path.join('van', 'reposync', 'README.txt'), 'r').read()
long_description += '\n'
long_description += open('CHANGES.txt', 'r').read()

setup(name="van.reposync",
      description='Mirror a pypi-style egg repository from a debian APT repository',
      long_description=long_description,
      author="Vanguardistas",
      url='http://pypi.python.org/pypi/van.reposync',
      version='1.0.1',
      license = 'ZPL 2.1',
      packages=find_packages(),
      entry_points = {'console_scripts': ['van-reposync = van.reposync:main',]},
      namespace_packages=["van"],
      install_requires=[
          'setuptools',
          'zc.lockfile',
          'van.pydeb',
          # 'apt >= 0.7.91', XXX not on pypi!
          ],
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'Intended Audience :: System Administrators',
                   'Topic :: System :: Archiving :: Packaging',
                   'License :: DFSG approved',
                   'License :: OSI Approved :: Zope Public License',
                   'Operating System :: POSIX :: Linux',
                   'Programming Language :: Python',
                   ],
      include_package_data = True,
      zip_safe = False,
      )
