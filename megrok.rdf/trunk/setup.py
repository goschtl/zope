from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='megrok.rdf',
      version=version,
      description="RDF based DB support for Grok.",
      long_description=open("README.txt").read(),
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
          'rdflib == 2.4.0'
         ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
