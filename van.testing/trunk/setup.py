##############################################################################
#
# Copyright (c) 2008 Vanguardistas LLC.
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

long_description = (
    '.. contents::\n\n'
    + open(os.path.join('van', 'testing', 'README.txt')).read()
    + '\n\n'
    + open(os.path.join('CHANGES.txt')).read()
    )

setup(name="van.testing",
      version='1.0.0dev',
      license = 'ZPL 2.1',
      url = 'http://pypi.python.org/pypi/van.timeformat',
      author="Vanguardistas LLC",
      description="Layers for zope.testing to simplify test setups",
      packages=find_packages(),
      namespace_packages=["van"],
      install_requires = [
          'setuptools',
          'zope.app.appsetup',
          'zope.testing',
          ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Testing',
        'Development Status :: 5 - Production/Stable',
        ],
      long_description=long_description,
      include_package_data = True,
      zip_safe = False,
      )
