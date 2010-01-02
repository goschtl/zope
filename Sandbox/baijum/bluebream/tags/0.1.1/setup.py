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

import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name="bluebream",
    version="0.1.1",
    author="Baiju M",
    author_email="baiju.m.mail@gmail.com",
    url="https://launchpad.net/bluebream",
    download_url="http://pypi.python.org/pypi/bluebream",
    description="Script to setup a Zope project directory.",
    long_description=(
        read('README.txt') 
        + '\n\n' +
        read('CHANGES.txt')
        + '\n\n' +
        'Download\n'
        '********'),
    license="Zope Public License",
    packages=find_packages("src"),
    package_dir={"": "src"},
    zip_safe=False,
    include_package_data=True,
    install_requires=["PasteScript>=1.7.3"],
    extras_require={"test": ["zc.buildout"]},
    entry_points={
    "paste.paster_create_template": ["bluebream = bluebream.template:BlueBream"]},
    )
