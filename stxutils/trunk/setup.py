##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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
from setuptools import setup


setup(name='stxutils',
      version='0.1dev',
      description='StructuredText utilities',
      long_description=(open('README.txt').read() + '\n\n' +
                        open('CHANGES.txt').read()
                       ),
      license='ZPL 2.1',
      packages=['stxutils'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
               'zope.structuredtext>=3.4.0',
               'docutils>=0.5',
      ],
      entry_points = """\
        [console_scripts]
        stx2html = stxutils.tohtml:main
        stx2rst = stxutils.torst:main
      """
     )
