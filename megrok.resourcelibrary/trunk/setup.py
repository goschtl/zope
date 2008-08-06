from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='megrok.resourcelibrary',
      version=version,
      description="static resource library support for Grok.",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Grok Team',
      author_email='grok-dev@zope.org',
      url='',
      license='ZPL',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['megrok'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'setuptools',
          'grok >= 0.13',
          'zc.resourcelibrary',
         ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
