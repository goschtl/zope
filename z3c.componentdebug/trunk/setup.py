from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='z3c.componentdebug',
      version=version,
      description="Provides a set of tools for inspecting ZCA component registries.",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='Python Zope',
      author='Ross Patterson',
      author_email='me@rpatterson.net',
      url='http://rpatterson.net/software/z3c.componentdebug',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
