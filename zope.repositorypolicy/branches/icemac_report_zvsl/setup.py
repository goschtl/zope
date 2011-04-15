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

setup(
    name='zope.repositorypolicy',
    version='0.1dev',
    author='Zope Foundation and Contributors',
    author_email='zope-dev@zope.org',
    url='http://pypi.python.org/pypi/zope.repositorypolicy',
    description="""\
        Tools to verify and help sustain policy compliance for projects in
        svn.zope.org
    """,
    long_description = '\n\n'.join([README, CHANGES]),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='ZPL 2.1',
    namespace_packages=['zope'],
    install_requires=[
        'setuptools',
        'subvertpy'],
    entry_points="""
        [console_scripts]
        zope-org-check-repos = zope.repositorypolicy.repository:main
        zope-org-check-repos-mail = zope.repositorypolicy.repository:main_mail
        zope-org-check-project = zope.repositorypolicy.project:main
        zope-org-fix-project = zope.repositorypolicy.copyright:main
    """)
