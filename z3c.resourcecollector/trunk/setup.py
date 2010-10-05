import os

from setuptools import setup, find_packages, Extension

setup(name='z3c.resourcecollector',
      version='1.1.3',
      url='http://launchpad.net/z3c.resourcecollector',
      license='ZPL',
      description='collects multiple resources and combines them to one',
      author='Zoltan Szabo',
      author_email='zoltan.szabo@informmedia.ro',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['z3c'],
      extras_require=dict(test=['zope.app.testing',
                                'zope.testing',
                                'z3c.testing',
                                'zope.testbrowser'
                                ]),
      install_requires=[
          'setuptools',
          'zope.app.appsetup',
          'zope.app.component',
          'zope.app.form',
          'zope.app.wsgi',
          'zope.cachedescriptors',
          'zope.component',
          'zope.configuration',
          'zope.interface',
          'zope.publisher',
          'zope.schema',
          'zope.security',
          'zope.viewlet',
          ],
      include_package_data = True,
      zip_safe = False,
      )
