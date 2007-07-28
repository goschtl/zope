#!python
from setuptools import setup, find_packages

setup(name='z3c.configurator',
      version='1.1.1',
      author = "Zope Community",
      author_email = "zope3-dev@zope.org",
      description = "Dynamic configuration",
      license = "ZPL 2.1",
      keywords = "zope zope3",
      url='http://svn.zope.org/z3c.configurator',
      zip_safe=False,
      packages=find_packages('src'),
      include_package_data=True,
      package_dir = {'':'src'},
      namespace_packages=['z3c'],
      extras_require = dict(test=['zope.app.testing']),
      install_requires = [
          'setuptools',
          'zope.annotation',
          'zope.app.pagetemplate',
          'zope.app.securitypolicy',
          'zope.app.testing',
          'zope.app.zcmlfiles',
          'zope.cachedescriptors',
          'zope.component',
          'zope.dublincore',
          'zope.formlib',
          'zope.i18nmessageid',
          'zope.interface',
          'zope.schema',
          'zope.testbrowser',
          'zope.testing',
          ],
      dependency_links=['http://download.zope.org/distribution']
      )

