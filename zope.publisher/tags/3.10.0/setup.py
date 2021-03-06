##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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
# This package is developed by the Zope Toolkit project, documented here:
# http://docs.zope.org/zopetoolkit
# When developing and releasing this package, please follow the documented
# Zope Toolkit policies as described by this documentation.
##############################################################################

from setuptools import setup, find_packages

entry_points = """
[paste.app_factory]
main = zope.publisher.paste:Application

[zope.publisher.publication_factory]
sample = zope.publisher.tests.test_paste:SamplePublication
"""

setup(name='zope.publisher',
      version = '3.10.0',
      url='http://pypi.python.org/pypi/zope.publisher',
      license='ZPL 2.1',
      author='Zope Corporation and Contributors',
      author_email='zope-dev@zope.org',
      description="The Zope publisher publishes Python objects on the web.",
      long_description=(open('README.txt').read()
                        + '\n\n'
                        + open('CHANGES.txt').read()),

      entry_points=entry_points,

      packages=find_packages('src'),
      package_dir={'': 'src'},

      namespace_packages=['zope',],
      tests_require=['zope.testing'],
      install_requires=['setuptools',
                        'zope.authentication',
                        'zope.browser',
                        'zope.component',
                        'zope.configuration',
                        'zope.contenttype',
                        'zope.event',
                        'zope.exceptions',
                        'zope.i18n',
                        'zope.interface',
                        'zope.location',
                        'zope.proxy',
                        'zope.security',
                       ],
      include_package_data=True,

      zip_safe=False,
      )
