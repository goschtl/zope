# -*- coding: utf-8 -*-
"""
This module contains the tool of z3c.recipe.eggbasket
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.4.0'

long_description = (
    'Change history\n'
    '**************\n'
    + '\n' + 
    read('CHANGES.txt')
    + '\n' +
    'Detailed Documentation\n'
    '**********************\n'
    + '\n' +
    read('z3c', 'recipe', 'eggbasket', 'README.txt')
    + '\n' +
    'Contributors\n' 
    '************\n'
    + '\n' +
    read('CONTRIBUTORS.txt')
    + '\n' +
    'Download\n'
    '********\n'
    )


setup(name='z3c.recipe.eggbasket',
      version=version,
      description="Install eggs from a tarball and create that egg.",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: Zope Public License',
        ],
      keywords='',
      author='Grok Team',
      author_email='grok-dev@zope.org',
      url='https://launchpad.net/grok',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['z3c', 'z3c.recipe'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'zc.buildout',
                        'zc.recipe.egg',
                        ],
      tests_require=['zope.testing', 'zc.recipe.egg'],
      test_suite='z3c.recipe.eggbasket.tests.test_docs.test_suite',
      entry_points={
        "zc.buildout":
            ["default = z3c.recipe.eggbasket:Downloader",
             "creator = z3c.recipe.eggbasket:Creator",],
        },
      )
