from setuptools import setup, find_packages
import os

version = '0.2'

setup(name='z3c.persistentfactory',
      version=version,
      description=(
          "Wrap instance methods in persistent factory wrappers for "
          "using instance methods as ZCA factories."), 
      long_description=(open(os.path.join(
          "z3c", "persistentfactory", "README.txt")).read() + "\n" +
                        open(os.path.join("docs", "HISTORY.txt")).read()),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Ross Patterson',
      author_email='me@rpatterson.net',
      url='http://pypi.python.org/pypi/z3c.persistentfactory',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['z3c'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'zope.interface',
          'zope.component',
          'ZODB3',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
