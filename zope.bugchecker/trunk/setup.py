##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
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

README = open('README.txt').read()
CHANGES = open('CHANGES.txt').read()

version = '0.1'

setup(name='zope.bugchecker',
      version=version,
      description="Check the Zope bugtracker for new bugs",
      long_description='\n\n'.join([README,CHANGES]),
      classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Framework :: Zope2",
        "Framework :: Zope3",
      ],
      keywords='zope launchpad bugchecker',
      author='Charlie Clark',
      author_email='',
      url='http://pypi.python.org/pypi/zope.bugchecker',
      license='ZPL 2.1',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'launchpadlib'
      ],
      entry_points="""
      [console_scripts]
      """,
)
