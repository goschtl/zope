from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='z3c.offlinepack',
      version=version,
      description="Pack ZODB databases without running Zope or ZEO",
      long_description="""\
Pack a ZODB storage without running any part of the Zope application
server.  Only an appropriate version of Zope for the ZODB storage is
required.  Use on a copy of a ZODB storage.  Do not run on a ZODB
storage currently in use.""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Ross Patterson',
      author_email='me@rpatterson.net',
      url='http://svn.zope.org/z3c.offlinepack',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['z3c'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'ZODB3', 'zope.dottedname'
      ],
      extras_require=dict(test=['zc.buildout', 'zc.recipe.egg']),
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      offlinepack = z3c.offlinepack:main
      """,
      )
