# -*- coding: utf-8 -*-

from os.path import join
from setuptools import setup, find_packages

name='megrok.z3cform.layout'
version = '0.2.1'
readme = open(join('src', 'megrok', 'z3cform', 'layout', 'README.txt')).read()
history = open(join('docs', 'HISTORY.txt')).read()

setup(name = name,
      version = version,
      description = "Generic templates for megrok.z3cform.base",
      long_description = readme + '\n\n' + history,
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='Grok Form Templates Layout',
      author='Souheil Chelfouh',
      author_email='trollfot@gmail.com',
      url='',
      license='GPL',
      package_dir={'': 'src'},
      packages=find_packages('src', exclude=['ez_setup']),
      namespace_packages=['megrok', 'megrok.z3cform'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'grokcore.view',
          'megrok.z3cform.base',
          'megrok.pagetemplate',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
