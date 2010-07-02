from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='zopyx.versioning',
      version=version,
      description="A flexible and pluggable versioning system for schema-oriented documents",
      long_description=open("zopyx/versioning/README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='Andreas Jung',
      author_email='info@zopyx.com',
      url='http://svn.plone.org/svn/collective/',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['zopyx'],
      include_package_data=True,
      zip_safe=False,
      test_runner='nose.testrunner',
      install_requires=[
          'setuptools',
          'zope.component',
          'pymongo',
          'unittest2',
          'anyjson',
          'nose',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
