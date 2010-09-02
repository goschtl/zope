# -*- coding: utf-8 -*-
"""
This module contains the tool of z3c.recipe.ldap
"""
import os
from setuptools import setup, find_packages

version = '0.2dev'

def read(*path):
    return open(os.path.join(*path)).read() + '\n\n'


long_description = (read('z3c', 'recipe', 'ldap', 'docs', 'README.txt') +
                    read('CHANGES.txt'))


entry_points = {"zc.buildout": ["default = z3c.recipe.ldap:Slapd",
                                "slapadd = z3c.recipe.ldap:Slapadd"]}

setup(name='z3c.recipe.ldap',
      version=version,
      description="Deploy an OpenLDAP server in a zc.buildout",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Ross Patterson',
      author_email='me@rpatterson.net',
      url='http://pypi.python.org/pypi/z3c.recipe.ldap',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['z3c', 'z3c.recipe'],
      include_package_data=True,
      zip_safe=True,
      install_requires=['setuptools',
                        'zc.buildout',
                        'zc.recipe.egg'
                        # -*- Extra requirements: -*-
                        ],
      entry_points=entry_points,
      )
