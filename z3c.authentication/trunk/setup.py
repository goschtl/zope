#!python
from setuptools import setup, find_packages

setup(name='z3c.authentication',
      version='0.1.0',
      author = "Zope Community",
      author_email = "zope3-dev@zope.org",
      license = "ZPL 2.1",
      keywords = "authentication zope zope3",
      url='http://svn.zope.org/z3c.authentication',

      zip_safe=False,
      packages=find_packages('src'),
      include_package_data=True,
      package_dir = {'':'src'},
      namespace_packages=['z3c',],
      install_requires=[
          'setuptools',
          'zope.component',
          'zope.configuration',
          'zope.contentprovider',
          'zope.i18n',
          'zope.interface',
          'zope.publisher',
          'zope.schema',
          'zope.app', # for zope.app.pagetemplate
          'zope.app.container',
          'z3c.i18n',
          ],
      extras_require={
          'test': ['zope.testing', 'zope.app.testing', 'z3c.configurator'],
          },
     )

