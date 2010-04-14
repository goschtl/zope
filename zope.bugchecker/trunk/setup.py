from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='zope.bugtracker',
      version=version,
      description="Check the Zope bugtracker for new bugs",
      long_description="""\
""",
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Charlie Clark',
      author_email='',
      url='',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=['launchpadlib'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
