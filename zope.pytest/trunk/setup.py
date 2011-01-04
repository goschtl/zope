from setuptools import setup, find_packages
import sys,os

version = '1.0'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read(os.path.join('README.txt'))
    + '\n' +
    read(os.path.join('CHANGES.txt'))
    + '\n' +
    'Download\n'
    '********\n'
    )

setup(name='zope.pytest',
      version=version,
      description="zope pytest integration",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='',
      author_email='',
      url='',
      license='BSD',
      packages=find_packages('src',exclude=['ez_setup']),
      namespace_packages=['zope'],
      package_dir={'': 'src'},
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zope.configuration',
          'zope.component',
          'zope.testing',
          'zope.event',
          'zope.processlifetime',
          'zope.app.publication',
          'zope.app.wsgi',
          'ZODB3',
          'WebOb',
          'simplejson'
          # -*- Extra requirements: -*-
      ],
      entry_points={
      }
      )
