##############################################################################
#
# Copyright (c) 2009 None.
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
"""Setup"""
from setuptools import setup, find_packages

setup (
    name = 'megrok.ootbviewlets',
    version = '0.1.0',
    author = u"Christian Klinger",
    author_email = u"cklinger@novareto.de",
    description = u"Some out of the Box Viewlets ready for grok using z3c.menu*",
    license = "GNU General Public License (GPL)",
    keywords = u"",
    url = "http://pypi.python.org/pypi/megrok.ootbviewlets",
    classifiers = [],
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = [u'megrok'],
    extras_require = {'docs': ['Sphinx'],
                      'test': ['z3c.coverage',
                      'zope.testing']},
    install_requires = [
        'setuptools',
	'z3c.menu.simple',
	'grok',
        ],
    zip_safe = False,
    entry_points = {},
    )
