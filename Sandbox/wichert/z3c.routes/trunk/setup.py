from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='z3c.routes',
      version=version,
      description="Routes for Zope",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Wichert Akkerman',
      author_email='wichert@wiggy.net',
      url='',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['z3c'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zope.app.publication',
          'zope.publisher',
          'zope.dottedname',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
