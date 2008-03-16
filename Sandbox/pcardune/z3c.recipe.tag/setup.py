#!/usr/bin/env python
# Check python version

import sys
if sys.version_info < (2, 4):
    print >> sys.stderr, '%s: need Python 2.4 or later.' % sys.argv[0]
    print >> sys.stderr, 'Your python is %s' % sys.version
    sys.exit(1)

import os
from setuptools import setup, find_packages

setup(
    name="z3c.recipe.tag",
    author="Ignas",
    description="Generate ctags from eggs for development.",
    version='0.1.0-dev',
    url='http://svn.zope.org/Sanbox/pcardune/z3c.recipe.tag/',
    license="ZPL",
    maintainer="Paul Carduner",
    maintainer_email="zope-dev@zope.org",
    platforms=["any"],
    classifiers=["Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: GNU General Public License (GPL)",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Zope"],
    package_dir={'': 'src'},
    packages=find_packages('src'),
    namespace_packages=['z3c','z3c.recipe'],
    install_requires=['setuptools',
                      'zc.buildout',
                      'zc.recipe.egg'],
    entry_points="""
    [zc.buildout]
    tags = z3c.recipe.tag:TagsMaker

    [console_scripts]
    build_tags = z3c.recipe.tag:build_tags
    """,
    zip_safe=False,
    include_package_data=True,
    )
