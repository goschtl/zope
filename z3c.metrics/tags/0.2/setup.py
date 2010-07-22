from setuptools import setup, find_packages
import os

version = '0.2'

setup(name='z3c.metrics',
      version=version,
      description="Index arbitrary values as scores for object metrics.",
      long_description=(
          '.. contents::\n\n' +
          open(os.path.join("z3c", "metrics", "README.txt")).read() +
          "\n" + open(os.path.join("docs", "HISTORY.txt")).read()),
      # Get more strings from
      # http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='zope zope3 index',
      author='Ross Patterson',
      author_email='me@rpatterson.net',
      url='http://pypi.python.org/pypi/z3c.metrics',
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
      extras_require=dict(
          zope2=[
              'Zope2',
              'Products.GenericSetup',
              ],
          test=[
              'zope.testing',
              'zope.configuration',
              'zope.app.component >= 3.9.0',
              'zope.app.folder',
              ]),

      entry_points="""
      # -*- Entry points: -*-
      """)
