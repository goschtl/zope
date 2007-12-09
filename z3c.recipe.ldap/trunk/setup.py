# -*- coding: utf-8 -*-
"""
This module contains the tool of z3c.recipe.ldap
"""
import os
from setuptools import setup, find_packages

version = '0.1'

README = os.path.join(os.path.dirname(__file__), 
                      'z3c',
                      'recipe',
                      'ldap', 'docs', 'README.txt')

long_description = open(README).read() + '\n\n' 

entry_points = {"zc.buildout": ["default = z3c.recipe.ldap:Slapd",
                                "slapadd = z3c.recipe.ldap:Slapadd"]}

setup(name='z3c.recipe.ldap',
      version=version,
      description="Deploy an OpenLDAP serve in a zc.buildout",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Ross Patterson',
      author_email='me@rpatterson.net',
      url='http://cheeseshop.python.org/pypi/z3c.recipe.ldap',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['z3c.recipe'],
      include_package_data=True,
      zip_safe=True,
      install_requires=['setuptools',
                        'zc.buildout',
                        'zc.recipe.egg'
                        # -*- Extra requirements: -*-
                        ],
      entry_points=entry_points,
      )
